import json
from unittest.mock import patch

from django.test import TestCase
from eth_tester import EthereumTester, PyEVMBackend
from eth_utils import to_wei, to_bytes
from web3 import EthereumTesterProvider, Web3

from ..tasks import event_listener
from .contracts.bank import BANK_ABI_RAW, BANK_BYTECODE
from .contracts.claim import CLAIM_ABI_RAW, CLAIM_BYTECODE
from ..chainevents import AbstractEventReceiver
from ..event_listener import EventListener
from ..models import MonitoredEvent, FailedEventLog, Daemon

# Keeps track of fired events
claim_events = []
bank_withdraw_events = []
bank_deposit_events = []


class ClaimEventReceiver(AbstractEventReceiver):
    def save(self, decoded_event):
        claim_events.append(decoded_event)


class BankWithdrawEventReceiver(AbstractEventReceiver):
    def save(self, decoded_event):
        bank_withdraw_events.append(decoded_event)


class BankDepositEventReceiver(AbstractEventReceiver):
    def save(self, decoded_event):
        bank_deposit_events.append(decoded_event)


class ErroneousBankDepositEventReceiver(AbstractEventReceiver):
    def save(self, decoded_event):
        raise ValueError


def patched_get_block_logs(*args, **kwargs):
    """Simulates a error raised by the web3 instance"""
    raise ValueError


class EventListenerTestCase(TestCase):
    def setUp(self):
        super(EventListenerTestCase, self).setUp()

    def tearDown(self):
        super(EventListenerTestCase, self).tearDown()

        # Clear event receivers state
        claim_events.clear()
        bank_deposit_events.clear()
        bank_withdraw_events.clear()

        # Reset to snapshot
        self.eth_tester.revert_to_snapshot(self.clean_state_snapshot)

    @classmethod
    def setUpTestData(cls):
        cls.eth_tester = EthereumTester(backend=PyEVMBackend())
        cls.provider = EthereumTesterProvider(cls.eth_tester)
        cls.web3 = Web3(cls.provider)

        # Deploy the Bank test contract
        cls.bank_abi = json.loads(BANK_ABI_RAW)
        bank_bytecode = BANK_BYTECODE

        Bank = cls.web3.eth.contract(abi=cls.bank_abi, bytecode=bank_bytecode)
        tx_hash = Bank.constructor().transact()
        tx_receipt = cls.web3.eth.waitForTransactionReceipt(tx_hash)
        cls.bank_address = tx_receipt.contractAddress
        cls.bank_contract = cls.web3.eth.contract(address=cls.bank_address, abi=cls.bank_abi)

        # Deploy the Claim test contract
        cls.claim_abi = json.loads(CLAIM_ABI_RAW)
        claim_bytecode = CLAIM_BYTECODE

        Claim = cls.web3.eth.contract(abi=cls.claim_abi, bytecode=claim_bytecode)
        tx_hash = Claim.constructor().transact()
        tx_receipt = cls.web3.eth.waitForTransactionReceipt(tx_hash)
        cls.claim_address = tx_receipt.contractAddress
        cls.claim_contract = cls.web3.eth.contract(address=cls.claim_address, abi=cls.claim_abi)

        # Take a snapshot of this state so far
        cls.clean_state_snapshot = cls.eth_tester.take_snapshot()

    def _create_deposit_event(self, event_receiver=None):
        if not event_receiver:
            event_receiver = 'django_ethereum_events.tests.test_event_listener.BankDepositEventReceiver'

        deposit_event = MonitoredEvent.objects.register_event(
            event_name='LogDeposit',
            contract_address=self.bank_address,
            contract_abi=self.bank_abi,
            event_receiver=event_receiver
        )

        return deposit_event

    def _create_withdraw_event(self, event_receiver=None):
        if not event_receiver:
            event_receiver = 'django_ethereum_events.tests.test_event_listener.BankWithdrawEventReceiver'

        withdraw_event = MonitoredEvent.objects.register_event(
            event_name='LogWithdraw',
            contract_address=self.bank_address,
            contract_abi=self.bank_abi,
            event_receiver=event_receiver
        )

        return withdraw_event

    def _create_claim_event(self, event_receiver=None):
        if not event_receiver:
            event_receiver = 'django_ethereum_events.tests.test_event_listener.ClaimEventReceiver'

        claim_event = MonitoredEvent.objects.register_event(
            event_name='ClaimSet',
            contract_address=self.claim_address,
            contract_abi=self.claim_abi,
            event_receiver=event_receiver
        )

        return claim_event

    def test_pending_blocks_fetched(self):
        last_block_proccesed = 0
        blocks_to_mine = 5
        current = self.web3.eth.blockNumber
        listener = EventListener(rpc_provider=self.provider)

        self.assertEqual(listener.get_pending_blocks(), list(range(last_block_proccesed + 1, current + 1)))
        listener.execute()
        last_block_proccesed = current

        # Mine some blocks
        self.eth_tester.mine_blocks(num_blocks=blocks_to_mine)
        current = self.web3.eth.blockNumber

        self.assertEqual(listener.get_pending_blocks(), list(range(last_block_proccesed + 1, current + 1)))
        listener.execute()

        # All blocks processed, verify once more
        self.assertEqual(listener.get_pending_blocks(), [])

    def test_monitor_contract_single_event_once(self):
        """Test the monitoring of a single event fired only once.
        """
        deposit_value = to_wei(1, 'ether')
        self._create_deposit_event()
        listener = EventListener(rpc_provider=self.provider)

        tx_hash = self.bank_contract.functions.deposit(). \
            transact({'from': self.web3.eth.accounts[0], 'value': deposit_value})

        listener.execute()

        self.assertEqual(len(bank_deposit_events), 1, "Deposit event listener fired")
        self.assertEqual(bank_deposit_events[0].args.amount, deposit_value, "Argument fetched correctly")

    def test_monitor_contract_single_event_twice_same_interval(self):
        """Test the monitoring of a single event fired twice before the execute method was called
        """

        deposit_value = to_wei(1, 'ether')
        self._create_deposit_event()
        listener = EventListener(rpc_provider=self.provider)

        tx_hash = self.bank_contract.functions.deposit(). \
            transact({'from': self.web3.eth.accounts[0], 'value': deposit_value})

        tx_hash = self.bank_contract.functions.deposit(). \
            transact({'from': self.web3.eth.accounts[0], 'value': 2 * deposit_value})

        listener.execute()

        self.assertEqual(len(bank_deposit_events), 2, "Deposit event listener fired twice")
        self.assertEqual(bank_deposit_events[1].args.amount, 2 * deposit_value, "Argument fetched correctly the twice")

    def test_monitor_contract_single_event_twice_different_interval(self):
        """Test the monitoring of a single event fired twice in the following fashion

            transaction
            execute()
            transaction
            execute()
        """

        deposit_value = to_wei(1, 'ether')
        self._create_deposit_event()
        listener = EventListener(rpc_provider=self.provider)

        tx_hash = self.bank_contract.functions.deposit(). \
            transact({'from': self.web3.eth.accounts[0], 'value': deposit_value})

        listener.execute()

        tx_hash = self.bank_contract.functions.deposit(). \
            transact({'from': self.web3.eth.accounts[0], 'value': 2 * deposit_value})

        listener.execute()

        self.assertEqual(len(bank_deposit_events), 2, "Deposit second event fetched")
        self.assertEqual(bank_deposit_events[1].args.amount, 2 * deposit_value, "Argument fetched correctly")

    def test_monitor_contract_multiple_events(self):
        """Test the monitoring of multiple events in the same smart contract
        """
        deposit_value = to_wei(1, 'ether')
        withdraw_value = deposit_value
        self._create_deposit_event()
        self._create_withdraw_event()

        listener = EventListener(rpc_provider=self.provider)

        tx_hash = self.bank_contract.functions.deposit(). \
            transact({'from': self.web3.eth.accounts[0], 'value': deposit_value})

        tx_hash = self.bank_contract.functions.withdraw(withdraw_value). \
            transact({'from': self.web3.eth.accounts[0]})

        listener.execute()

        self.assertEqual(len(bank_deposit_events), 1, "Deposit event fired")
        self.assertEqual(len(bank_withdraw_events), 1, "Withdraw event fired")

    def test_monitor_multiple_contracts_multiple_events(self):
        """Test the monitoring of multiple events in multiple smart contracts
        """
        deposit_value = to_wei(1, 'ether')
        withdraw_value = deposit_value
        key = "hello"
        value = "world"
        self._create_deposit_event()
        self._create_withdraw_event()
        self._create_claim_event()

        listener = EventListener(rpc_provider=self.provider)

        tx_hash = self.bank_contract.functions.deposit(). \
            transact({'from': self.web3.eth.accounts[0], 'value': deposit_value})

        tx_hash = self.bank_contract.functions.withdraw(withdraw_value). \
            transact({'from': self.web3.eth.accounts[0]})

        tx_hash = self.claim_contract.functions.setClaim(to_bytes(text=key), to_bytes(text=value)). \
            transact({'from': self.web3.eth.accounts[0]})

        listener.execute()

        self.assertEqual(len(bank_deposit_events), 1, "Deposit event fired")
        self.assertEqual(len(bank_withdraw_events), 1, "Withdraw event fired")
        self.assertEqual(len(claim_events), 1, "Claim event fired")

    def test_monitor_event_monitored_from_value(self):
        """Test the added events are tracked from the next block that is ready to be processed
        """
        current = self.web3.eth.blockNumber
        deposit_value = to_wei(1, 'ether')

        listener = EventListener(rpc_provider=self.provider)
        listener.execute()

        event = self._create_deposit_event()

        tx_hash = self.bank_contract.functions.deposit(). \
            transact({'from': self.web3.eth.accounts[0], 'value': deposit_value})

        # intention is to the the .monitored_from field, not the cache / update mechanism
        # this is why we get a new instance of the event listener
        listener = EventListener(rpc_provider=self.provider)
        listener.execute()
        event.refresh_from_db()

        self.assertEqual(len(bank_deposit_events), 1, "Deposit event listener fired")
        self.assertEqual(event.monitored_from, current + 1)

    def test_monitor_event_listener_state_update_event_added(self):
        """Test the addition of a newly created event inside the event listener decoder state
        """
        current = self.web3.eth.blockNumber
        deposit_value = to_wei(1, 'ether')

        listener = EventListener(rpc_provider=self.provider)
        listener.execute()

        event = self._create_deposit_event()  # this will fire a signal which will update a cache value

        tx_hash = self.bank_contract.functions.deposit(). \
            transact({'from': self.web3.eth.accounts[0], 'value': deposit_value})

        listener.execute()  # updated cache value from previous line will force data to be re-fetched from the backend
        event.refresh_from_db()

        self.assertEqual(len(bank_deposit_events), 1, "Deposit event listener fired")
        self.assertEqual(event.monitored_from, current + 1)

    def test_erroneous_event_receiver_impl(self):
        self._create_deposit_event(
            event_receiver='django_ethereum_events.tests.test_event_listener.ErroneousBankDepositEventReceiver')

        deposit_value = to_wei(1, 'ether')

        tx_hash = self.bank_contract.functions.deposit(). \
            transact({'from': self.web3.eth.accounts[0], 'value': deposit_value})

        listener = EventListener(rpc_provider=self.provider)
        listener.execute()

        failed_events = FailedEventLog.objects.all()
        self.assertEqual(listener.daemon.block_number, self.web3.eth.blockNumber,
                         "Exception did not cause listener to stop")
        self.assertEqual(failed_events.count(), 1, "Failed event log created")
        stored_args = json.loads(failed_events.first().args)
        self.assertEqual(stored_args['amount'], deposit_value, "Failed event log saved correct arguments")

    def test_event_listener_task(self):
        """Test that the event listener task is working as intended"""
        deposit_value = to_wei(1, 'ether')
        event = self._create_deposit_event()

        tx_hash = self.bank_contract.functions.deposit(). \
            transact({'from': self.web3.eth.accounts[0], 'value': deposit_value})

        current = self.web3.eth.blockNumber
        event_listener()

        daemon = Daemon.get_solo()
        self.assertEqual(daemon.block_number, current, 'Task run successfully')
        self.assertEqual(daemon.last_error_block_number, 0, 'No errors during task execution')

    def test_event_listener_task_exception_raised(self):
        """Determine if the event listener task correctly sets the daemon.last_error_block_number
        when an exception occurs that is unhandled.

        """
        current = self.web3.eth.blockNumber
        event_listener()
        daemon = Daemon.get_solo()

        self.assertEqual(daemon.block_number, current, 'Task run successfully')
        self.assertEqual(daemon.last_error_block_number, 0, 'No errors during task execution')

        # Create a new monitored event, run the task again but with the `get_block_logs` method patched
        # to simulate an error raised from the web3 instance (e.g. rcp node is down)
        deposit_value = to_wei(1, 'ether')
        event = self._create_deposit_event()

        tx_hash = self.bank_contract.functions.deposit(). \
            transact({'from': self.web3.eth.accounts[0], 'value': deposit_value})

        with patch.object(EventListener, 'get_block_logs', patched_get_block_logs):
            event_listener()

        daemon.refresh_from_db()
        self.assertEqual(daemon.block_number, current, 'Erroneous block was not processed')
        self.assertEqual(daemon.last_error_block_number, current + 1, 'Error block was updated')

