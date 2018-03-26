from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.six import with_metaclass

from .decoder import Decoder
from .models import Daemon
from .singleton import Singleton
from .web3_service import Web3Service


class EventListener(with_metaclass(Singleton)):
    """Event Listener class."""

    def __init__(self, *args, **kwargs):
        super(EventListener, self).__init__()
        self.decoder = Decoder()
        self.web3 = Web3Service(*args, **kwargs).web3

    def get_pending_blocks(self):
        """
        Retrieve the blocks that have not been processed.

        Returns:
            An iterable of (from, to) tuples, containing
            the unprocessed block numbers.

        """
        daemon = Daemon.get_solo()
        current = self.web3.eth.blockNumber
        step = getattr(settings, "ETHEREUM_LOGS_BATCH_SIZE", 10000)
        if daemon.block_number < current:
            return (
                (r, min(current, r + step))
                for r in range(daemon.block_number + 1, current + 1, step)
            )
        return []

    def update_block_number(self, block_number):
        """Updates the internal block_number counter."""
        daemon = Daemon.get_solo()
        daemon.block_number = block_number
        daemon.save()

    def get_logs(self, from_block, to_block):
        """
        Retrieves the relevant log entries from the given block range.

        Args:
            from_block (int): The first block number.
            to_block (int): The last block number.

        Returns:
            The list of relevant log entries.

        """
        # Note: web3.eth.getLogs is not implemented in web3 3.x
        # And even in web3 4.0.x betas it's missing in test RPC implementation
        addresses = self.decoder.watched_addresses
        if len(addresses) == 1:
            # Ganache (aka ethereumjs-testrpc) doesn't support multiple addrs.
            # This is to help simple tests pass if there's only one entry.
            # If you have multiple contracts and test against Ganache,
            # it's not this library's fault no events are found.
            addresses = addresses[0]
        log_filter = self.web3.eth.filter({
            "fromBlock": hex(from_block),
            "toBlock": hex(to_block),
            "address": addresses,
            "topics": self.decoder.topics,
        })
        if hasattr(log_filter, "get_all_entries"):
            logs = log_filter.get_all_entries()
        else:
            logs = self.web3.eth.getFilterLogs(log_filter.filter_id)
        self.web3.eth.uninstallFilter(log_filter.filter_id)
        return logs

    def save_events(self, decoded_logs):
        """
        Fires the appropriate event receivers for every given log.

        Args:
            decoded_logs (:obj:`list` of :obj:`dict`): The decoded logs.

        """
        for topic, decoded_log in decoded_logs:
            event_receiver_cls = import_string(
                self.decoder.topics_map[topic]['EVENT_RECEIVER']
            )
            event_receiver_cls().save(decoded_event=decoded_log)

    def execute(self):
        """Program loop, does all the underlying work."""
        pending_blocks = self.get_pending_blocks()
        for from_block, to_block in pending_blocks:
            logs = self.get_logs(from_block, to_block)
            decoded_logs = self.decoder.decode_logs(logs)
            self.save_events(decoded_logs)
            self.update_block_number(to_block)
