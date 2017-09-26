import logging
from django.conf import settings
from django.utils.module_loading import import_string
from ethereum.utils import sha3
from web3.utils.events import get_event_data
from eth_utils import encode_hex
from .singleton import Singleton

logger = logging.getLogger(__name__)


class Decoder(metaclass=Singleton):
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
        method_header = None
        if item.get(u'inputs'):
            # Generate methodID and link it with the abi
            method_header = "{}({})".format(item[u'name'], ','.join(
                map(lambda input_arg: input_arg[u'type'], item[u'inputs'])))
        else:
            method_header = "{}()".format(item[u'name'])
        return encode_hex(sha3(method_header))

    def decode_log(self, log):
        log_topic = log['topics'][0]
        return log_topic, get_event_data(self.topics_map[log_topic]['EVENT_ABI'], log)

    def decode_logs(self, logs):
        decoded = []
        for log in logs:
            try:
                decoded.append(self.decode_log(log))
            except Exception as e:
                logger.error(str(e))
        return decoded
