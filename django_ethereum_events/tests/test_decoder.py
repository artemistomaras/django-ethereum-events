import json
from copy import deepcopy

from django.test import TestCase
from eth_tester import EthereumTester, PyEVMBackend
from eth_utils import to_wei
from hexbytes import HexBytes
from web3 import EthereumTesterProvider, Web3

from django_ethereum_events.models import MonitoredEvent
from django_ethereum_events.tests.contracts.bank import BANK_ABI_RAW, BANK_BYTECODE
from ..decoder import Decoder


class DecoderTestCase(TestCase):
    events_log_file = 'django_ethereum_events/tests/deposit_event_log.json'

    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        super(DecoderTestCase, self).tearDown()

        # Reset to snapshot
        self.eth_tester.revert_to_snapshot(self.clean_state_snapshot)

    @classmethod
    def setUpTestData(cls):
        super(DecoderTestCase, cls).setUpTestData()

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

        # Take a snapshot of this state so far
        cls.clean_state_snapshot = cls.eth_tester.take_snapshot()

        # Log contains a LogDeposit event with the following arguments
        # owner: self.web3.eth.accounts[0]
        # amount: 1 ether
        with open(cls.events_log_file) as log_file:
            test_logs = json.load(log_file)

        # From web3 v3 to web3 v4, the topics as we as the blockHash, transactionHash are
        # wrapped with the HexBytes class.
        cls.logs = cls._proccess_logs(test_logs)

    @staticmethod
    def _proccess_logs(test_logs):
        logs = deepcopy(test_logs)
        for index, log in enumerate(test_logs):
            # Convert topics to HexBytes
            for z, topic in enumerate(log['topics']):
                logs[index]['topics'][z] = HexBytes(topic)

            # Convert blockHash and transactionHash to HexBytes
            logs[index]['transactionHash'] = HexBytes(log['transactionHash'])
            logs[index]['blockHash'] = HexBytes(log['blockHash'])
        return logs

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

    def test_monitored_event_fetched_from_backend(self):
        """Test that the decoder is in sync with the backend
        """
        self._create_deposit_event()
        decoder = Decoder(block_number=0)

        self.assertEqual(decoder.monitored_events.count(), 1, "LogDeposit is been monitored")

    def test_monitored_event_removed_from_backend(self):
        """Test the functionality of the refresh_state method
        """
        self._create_deposit_event()
        decoder = Decoder(block_number=0)

        self.assertEqual(decoder.monitored_events.count(), 1, "LogDeposit is been monitored")

        MonitoredEvent.objects.all().delete()
        decoder.refresh_state(block_number=1)

        self.assertEqual(decoder.monitored_events.count(), 0, "No events to monitor")

    def test_decode_logs(self):
        """Verify that the decoder correctly decodes the test logs.
        """
        self._create_deposit_event()
        decoder = Decoder(block_number=0)

        decoded_logs = decoder.decode_logs(self.logs)

        self.assertEqual(len(decoded_logs), 1, "Log decoded")
        self.assertEqual(decoded_logs[0][1].args.amount, to_wei(1, 'ether'), "Log `amount` parameter is correct")
        self.assertEqual(decoded_logs[0][1].args.owner, '0x82A978B3f5962A5b0957d9ee9eEf472EE55B42F1', "Log `owner` parameter is correct")
