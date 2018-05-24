import json
from copy import deepcopy

from django.conf import settings
from django.test import TestCase

from eth_utils import encode_hex, keccak
from hexbytes import HexBytes

from web3.utils.events import get_event_data

from ..decoder import Decoder


class DecoderTestCase(TestCase):
    event_signature = 'Deposit(address,bytes32,uint256)'

    def setUp(self):
        TestCase.setUp(self)

    @classmethod
    def setUpTestData(cls):  # noqa: N802
        super(DecoderTestCase, cls).setUpTestData()
        cls.decoder = Decoder()
        with open('django_ethereum_events/tests/event_logs.json') as log_file:
            test_logs = json.load(log_file)

        # From web3 v3 to web3 v4, the topics as we as the blockHash, transactionHash are
        # wrapped with the HexBytes class.
        cls.logs = deepcopy(test_logs)
        for index, log in enumerate(test_logs):
            for z, topic in enumerate(log['topics']):
                cls.logs[index]['topics'][z] = HexBytes(topic)

    def test_get_topic(self):
        self.assertEqual(len(self.decoder.topics), 1)
        self.assertEqual(
            self.decoder.topics[0],
            encode_hex(keccak(text=self.event_signature))
        )
        inline_dict = {self.decoder.topics[0]: settings.ETHEREUM_EVENTS[0]}
        self.assertDictEqual(
            self.decoder.topics_map, inline_dict,
            'Event dictionary not loaded in memory'
        )

    def test_get_log(self):
        topic, decoded_log = self.decoder.decode_log(self.logs[0])
        self.assertEqual(topic, encode_hex(keccak(text=self.event_signature)))
        self.assertEqual(decoded_log, get_event_data(
            settings.ETHEREUM_EVENTS[0]['EVENT_ABI'], self.logs[0]))

    def test_get_logs(self):
        decoded_logs = self.decoder.decode_logs(self.logs)
        self.assertEqual(
            len(decoded_logs), len(self.logs),
            'Decoded log line number mismatch'
        )
