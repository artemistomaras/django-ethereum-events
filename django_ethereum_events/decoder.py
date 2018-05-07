import logging

from django.conf import settings
from django.utils.six import with_metaclass

from eth_utils import encode_hex, keccak

from web3.utils.events import get_event_data

from .singleton import Singleton

logger = logging.getLogger(__name__)


def force_hex(value):
    """
    Given a :obj:`str` or :obj:`bytes`, always returns a hex string.

    This ensures consistency between Web3 3.x which uses :obj:`str`,
    and 4.x which uses :obj:`bytes` subclass :obj:`HexBytes`.
    """
    if isinstance(value, bytes):
        value = value.hex()
        if not value.startswith("0x"):
            value = "0x" + value
    return value


class Decoder(with_metaclass(Singleton)):
    """
    Transaction decoder implementation.

    Attributes:
        watched_addresses (:obj:`list` of :obj:`str`): List of contract
            addresses that are monitored for event logs.
        topics (:obj:`list` of :obj:`str`): Relevant topics (keccak hash).
        topics_map (:obj:`dict`): Maps topics to `settings.ETHEREUM_EVENTS`
            entries.

    """

    watched_addresses = []
    topics = []
    topics_map = {}

    def __init__(self, *args, **kwargs):
        super(Decoder, self).__init__(*args, **kwargs)
        for event in settings.ETHEREUM_EVENTS:
            topic = force_hex(self.get_topic(event['EVENT_ABI']))
            address = event['CONTRACT_ADDRESS']
            self.topics.append(topic)
            self.topics_map[topic] = event
            if address not in self.watched_addresses:
                self.watched_addresses.append(address)

    def get_topic(self, item):
        """
        Retrieve the keccak hash of the event abi.

        Args:
            item (:obj:`dict`): `settings.ETHEREUM_EVENTS` entry.

        Returns:
            str: the hex encoded keccak topic signature.

        """
        if item.get('inputs'):
            method_header = "{name}({args})".format(
                name=item['name'],
                args=','.join(
                    input_arg['type'] for input_arg in item['inputs']
                )
            )
        else:
            method_header = "{name}()".format(name=item['name'])
        return encode_hex(keccak(method_header))

    def decode_log(self, log):
        """
        Decodes a retrieved relevant log.

        Decoding is performed with the `web3.utils.events.get_event_data`
        function.

        Args:
            log (:obj:`dict`): the event log to decode
        Returns:
            The decoded log.

        """
        log_topic = force_hex(log['topics'][0])
        event_abi = self.topics_map[log_topic]['EVENT_ABI']
        return log_topic, get_event_data(event_abi, log)

    def decode_logs(self, logs):
        """
        Decode the given logs.

        Args:
            logs (:obj:`list` of :obj:`dict`): The targeted logs.
        Returns:
            The decoded logs.

        """
        decoded = []
        for log in logs:
            try:
                decoded.append(self.decode_log(log))
            except Exception as e:
                logger.exception(str(e))
        return decoded
