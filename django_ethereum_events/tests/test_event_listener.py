import json

from django.test import TestCase
from eth_tester import EthereumTester, PyEthereum21Backend
from eth_utils import to_wei
from web3 import EthereumTesterProvider, Web3

from ..chainevents import AbstractEventReceiver
from ..event_listener import EventListener
from ..models import MonitoredEvent
from .contracts.bank import BANK_ABI_RAW, BANK_BYTECODE
from .contracts.claim import CLAIM_ABI_RAW, CLAIM_BYTECODE

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
        cls.eth_tester = EthereumTester(backend=PyEthereum21Backend())
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


    # def test_monitor_contract_single_event_once(self):
    #     """Test the monitoring of a single event fired only once.
    #     """
    #     deposit_value = to_wei(1, 'ether')
    #     self._create_deposit_event()
    #     listener = EventListener(rpc_provider=self.provider)
    #
    #     tx_hash = self.bank_contract.functions.deposit().\
    #         transact({'from': self.web3.eth.accounts[0], 'value': deposit_value})
    #
    #     listener.execute()
    #
    #     self.assertEqual(len(bank_deposit_events), 1, "Deposit event listener fired")
    #     self.assertEqual(bank_deposit_events[0].args.amount, deposit_value, "Argument fetched correctly")
    #
    # def test_monitor_contract_single_event_twice_same_interval(self):
    #     """Test the monitoring of a single event fired twice before the execute method was called
    #     """
    #
    #     deposit_value = to_wei(1, 'ether')
    #     self._create_deposit_event()
    #     listener = EventListener(rpc_provider=self.provider)
    #
    #     tx_hash = self.bank_contract.functions.deposit().\
    #         transact({'from': self.web3.eth.accounts[0], 'value': deposit_value})
    #
    #     tx_hash = self.bank_contract.functions.deposit().\
    #         transact({'from': self.web3.eth.accounts[0], 'value': 2 * deposit_value})
    #
    #     listener.execute()
    #
    #     self.assertEqual(len(bank_deposit_events), 2, "Deposit event listener fired twice")
    #     self.assertEqual(bank_deposit_events[1].args.amount, 2 * deposit_value, "Argument fetched correctly the twice")
    #
    # def test_monitor_contract_single_event_twice_different_interval(self):
    #     """Test the monitoring of a single event fired twice as such:
    #
    #         transaction
    #         execute()
    #         transaction
    #         execute()
    #     """
    #
    #     deposit_value = to_wei(1, 'ether')
    #     self._create_deposit_event()
    #     listener = EventListener(rpc_provider=self.provider)
    #
    #     tx_hash = self.bank_contract.functions.deposit().\
    #         transact({'from': self.web3.eth.accounts[0], 'value': deposit_value})
    #
    #     listener.execute()
    #
    #     tx_hash = self.bank_contract.functions.deposit().\
    #         transact({'from': self.web3.eth.accounts[0], 'value': 2 * deposit_value})
    #
    #     listener.execute()
    #
    #     self.assertEqual(len(bank_deposit_events), 2, "Deposit second event fetched")
    #     self.assertEqual(bank_deposit_events[1].args.amount, 2 * deposit_value, "Argument fetched correctly")