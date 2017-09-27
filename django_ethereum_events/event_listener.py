from .decoder import Decoder
from .models import Daemon
from .singleton import Singleton
from .web3_service import Web3Service
from .exceptions import UnknownBlock
from django.utils.module_loading import import_string


class EventListener(metaclass=Singleton):
    """Event Listener class."""

    def __init__(self, *args, **kwargs):
        super(EventListener, self).__init__()
        self.decoder = Decoder()
        self.web3 = Web3Service(*args, **kwargs).web3

    def get_pending_blocks(self):
        """Retrieve the blocks that have not been processed.

        Returns:
            List containing the unprocessed block numbers.
        """
        blocks_to_process = []
        daemon = Daemon.get_solo()
        current = self.web3.eth.blockNumber
        if daemon.block_number < current:
            blocks_to_process = range(daemon.block_number + 1, current + 1)
        return blocks_to_process

    def update_block_number(self, block_number):
        """Updates the internal block_number counter."""
        daemon = Daemon.get_solo()
        daemon.block_number = block_number
        daemon.save()

    def get_logs(self, block_number):
        """Retrieves the relevant log entries from the given block.

        Args:
            block_number (int): The block number of the block to process.

        Returns:
            The list of relevant log entries.
        """
        block = self.web3.eth.getBlock(block_number)
        relevant_logs = []
        if block and block.get('hash'):
            for tx in block['transactions']:
                receipt = self.web3.eth.getTransactionReceipt(tx)
                for log in receipt.get('logs', []):
                    if log['address'] in self.decoder.watched_addresses and \
                            log['topics'][0] in self.decoder.topics:
                        relevant_logs.append(log)
            return relevant_logs, block
        else:
            raise UnknownBlock

    def save_events(self, decoded_logs):
        """Fires the appropriate event receivers for every given log.

        Args:
            decoded_logs (:obj:`list` of :obj:`dict`): The decoded logs.
        """
        for topic, decoded_log in decoded_logs:
            EventReceiver = import_string(
                self.decoder.topics_map[topic]['EVENT_RECEIVER'])
            EventReceiver().save(decoded_event=decoded_log)

    def execute(self):
        """Program loop, does all the underlying work."""
        pending_blocks = self.get_pending_blocks()
        for block_number in pending_blocks:
            logs, _ = self.get_logs(block_number)

            decoded_logs = self.decoder.decode_logs(logs)
            self.save_events(decoded_logs)

        if len(pending_blocks):
            self.update_block_number(pending_blocks[-1])
