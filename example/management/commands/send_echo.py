from django.conf import settings
from django.core.management import BaseCommand
from web3 import Web3, HTTPProvider

from example.management.commands.register_events import echo_address, echo_abi


class Command(BaseCommand):
    def handle(self, *args, **options):
        web3 = Web3(HTTPProvider('http://localhost:8545'))
        echo_contract = web3.eth.contract(echo_address, abi=echo_abi)
        txn_hash = echo_contract.functions.echo("hello").transact({'from': settings.WALLET_ADDRESS})
        print('Received txn_hash={} ...'.format(txn_hash))
        print('Waiting for transaction receipt...')
        txn_receipt = web3.eth.waitForTransactionReceipt(txn_hash)
        print('Received transaction receipt: {}'.format(txn_receipt))
