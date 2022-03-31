import logging

from web3 import Web3
from web3._utils.events import get_event_data

from django_ethereum_events.models import MonitoredEvent

logger = logging.getLogger(__name__)


class Decoder:
    """Event log decoder.

    Attributes:
        monitored_events (QuerySet): retrieved monitored events
        monitored_events: dict (address, topic) => monitored_event

    """

    monitored_events = None
    watched_addresses = []
    topics = {}

    def __init__(self, block_number, *args, **kwargs):
        super(Decoder, self).__init__(*args, **kwargs)
        self.refresh_state(block_number)
        self.web3 = Web3()

    def refresh_state(self, block_number):
        """Fetches the monitored events from the database and updates the decoder state variables.

        Args:
            block_number (int): next block to process

        """
        self.watched_addresses.clear()
        self.topics.clear()
        self.monitored_events = {}  # dict (address, topic) => [monitored_event1, monitored_event2, ...]

        for monitored_event in MonitoredEvent.objects.all():
            self.monitored_events[
                (monitored_event.contract_address, monitored_event.topic)
            ] = monitored_event

            if monitored_event.monitored_from is None:
                monitored_event.monitored_from = block_number
                monitored_event.save()

    def decode_log(self, log):
        """
        Decodes a retrieved relevant log.

        Decoding is performed with the `web3.utils.events.get_event_data`
        function.

        Args:
            log (AttributeDict): the event log to decode
        Returns:
            The decoded log.

        """
        log_topic = log['topics'][0].hex()
        address = log['address']
        mon_evt = self.monitored_events.get((address, log_topic), None)
        if mon_evt is None:
            return None  # combination of (address, topic) not monitored
        event_abi = mon_evt.event_abi_parsed
        decoded_log = get_event_data(self.web3.codec, event_abi, log)
        return (address, log_topic), decoded_log

    def decode_logs(self, logs):
        """Decode the given logs.

        Args:
            logs (list): The targeted logs to decode.
        Returns:
            list: the decoded logs

        """
        ret = []
        for log in logs:
            decoded = self.decode_log(log)
            if decoded is not None:
                ret.append(decoded)
        return ret
