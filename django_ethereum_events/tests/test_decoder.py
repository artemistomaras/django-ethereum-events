import json
from django.test import TestCase
from django.conf import settings
from web3.utils.events import get_event_data
from ethereum.utils import sha3
from eth_utils import encode_hex
from ..decoder import Decoder


class DecoderTestCase(TestCase):
    event_signature = 'Deposit(address,bytes32,uint256)'

    def setUp(self):
        TestCase.setUp(self)

    @classmethod
    def setUpTestData(cls):
        super(DecoderTestCase, cls).setUpTestData()
        cls.decoder = Decoder()
        cls.test_logs = json.load(open('django_ethereum_events/tests/event_logs.json'))

    def test_get_topic(self):
        self.assertEqual(len(self.decoder.topics), 1)
        self.assertEqual(self.decoder.topics[0], encode_hex(sha3(self.event_signature)))
        inline_dict = {}
        inline_dict[self.decoder.topics[0]] = settings.ETHEREUM_EVENTS[0]
        self.assertDictEqual(self.decoder.topics_map, inline_dict, 'Dictionary loaded in memory')

    def test_get_log(self):
        topic, decoded_log = self.decoder.decode_log(self.test_logs[0])
        self.assertEqual(topic, encode_hex(sha3(self.event_signature)))
        self.assertEqual(decoded_log, get_event_data(
            settings.ETHEREUM_EVENTS[0]['EVENT_ABI'], self.test_logs[0]))

    def test_get_logs(self):
        decoded_logs = self.decoder.decode_logs(self.test_logs)
        self.assertEqual(len(decoded_logs), len(self.test_logs), 'Every log decoded')
