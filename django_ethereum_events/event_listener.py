import itertools

from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.six import with_metaclass

from .decoder import Decoder
from .exceptions import UnknownBlock
from .models import Daemon
from .singleton import Singleton
from .web3_service import Web3Service


class EventListener():
    """Event Listener class."""

    def __init__(self, *args, **kwargs):
        super(EventListener, self).__init__()
        self.daemon = Daemon.get_solo()
        self.decoder = Decoder(block_number=self.daemon.block_number)
        self.web3 = Web3Service(*args, **kwargs).web3

    def get_pending_blocks(self):
        """
        Retrieve the blocks that have not been processed.

        Returns:
            An iterable of (from, to) tuples, containing
            the unprocessed block numbers.

        """
        pending_blocks = []
        current = self.web3.eth.blockNumber
        print('Current block in chain: {}'.format(current))
        step = getattr(settings, "ETHEREUM_LOGS_BATCH_SIZE", 10000)
        print('Last block proccessed: {}'.format(self.daemon.block_number))
        if self.daemon.block_number < current:
            start = self.daemon.block_number + 1
            pending_blocks = list(range(start, min(current, start + step) + 1))

        print('Got pending blocks: {}'.format(pending_blocks))
        return pending_blocks

    def update_block_number(self, block_number):
        """Updates the internal block_number counter."""
        self.daemon.block_number = block_number
        self.daemon.save()

    def get_block_logs(self, block_number):
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
                    address = log['address']
                    if address in self.decoder.watched_addresses and \
                            log['topics'][0].hex() in self.decoder.topics:
                        relevant_logs.append(log)
            return relevant_logs
        else:
            raise UnknownBlock

    def get_logs(self, from_block, to_block):
        """
        Retrieves the relevant log entries from the given block range.

        Args:
            from_block (int): The first block number.
            to_block (int): The last block number.

        Returns:
            The list of relevant log entries.

        """
        logs = itertools.chain.from_iterable(
            self.get_block_logs(n) for n in range(from_block, to_block + 1))
        return list(logs)

    def save_events(self, decoded_logs):
        """
        Fires the appropriate event receivers for every given log.

        Args:
            decoded_logs (:obj:`list` of :obj:`dict`): The decoded logs.

        """
        for topic, decoded_log in decoded_logs:
            event_receiver_cls = import_string(self.decoder.topics[topic].event_receiver)
            event_receiver_cls().save(decoded_event=decoded_log)

    def execute(self):
        """Program loop, does all the underlying work."""
        pending_blocks = self.get_pending_blocks()
        for block in pending_blocks:
            print('Processing block: {}'.format(block))
            logs = self.get_block_logs(block)
            decoded_logs = self.decoder.decode_logs(logs)
            self.save_events(decoded_logs)
            self.update_block_number(block)
