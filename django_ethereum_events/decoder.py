import logging
from django.conf import settings
from ethereum.utils import sha3
from web3.utils.events import get_event_data
from eth_utils import encode_hex
from .singleton import Singleton

logger = logging.getLogger(__name__)


class Decoder(metaclass=Singleton):
    """Transaction decoder implementation.

    Attributes:
        watched_addresses (:obj:`list` of :obj:`str`): List of contract addresses that
            are monitored for event logs.
        topics (:obj:`list` of :obj:`str`): Relevant topics (sha3 hash).
        topics_map (:obj:`dict`): Maps topics to `settings.ETHEREUM_EVENTS` entries.
    """
    watched_addresses = []
    topics = []
    topics_map = {}

    def __init__(self, *args, **kwargs):
        super(Decoder, self).__init__(*args, **kwargs)
        for event in settings.ETHEREUM_EVENTS:
            topic = self.get_topic(event['EVENT_ABI'])
            self.topics.append(topic)
            self.topics_map[topic] = event
            self.watched_addresses.append(event['CONTRACT_ADDRESS'])

    def get_topic(self, item):
        """Retrieve the sha3 hash of the event abi.

        Args:
            item (:obj:`dict`): `settings.ETHEREUM_EVENTS` entry.

        Returns:
            str: the hex encoded sha3 topic signature.
        """
        method_header = None
        if item.get(u'inputs'):
            method_header = "{}({})".format(item[u'name'], ','.join(
                map(lambda input_arg: input_arg[u'type'], item[u'inputs'])))
        else:
            method_header = "{}()".format(item[u'name'])
        return encode_hex(sha3(method_header))

    def decode_log(self, log):
        """Decodes a retrieved relevant log.

        Decoding is performed with the `web3.utils.events.get_event_data` function.

        Args:
            log (:obj:`dict`): the event log to decode
        Returns:
            The decoded log.
        """

        log_topic = log['topics'][0]
        return log_topic, get_event_data(self.topics_map[log_topic]['EVENT_ABI'], log)

    def decode_logs(self, logs):
        """Decode the given logs.

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
                logger.error(str(e))
        return decoded
