from django.conf import settings
from web3 import Web3, RPCProvider

from .singleton import Singleton


class Web3Service(metaclass=Singleton):
    def __init__(self, *args, **kwargs):
        super(Web3Service, self).__init__()
        rpc_provider = kwargs.pop('rpc_provider', None)
        if not rpc_provider:
            rpc_provider = RPCProvider(
                host=settings.ETHEREUM_NODE_HOST,
                port=settings.ETHEREUM_NODE_PORT,
                ssl=settings.ETHEREUM_NODE_SSL
            )
        self.web3 = Web3(rpc_provider)
        super(Web3Service, self).__init__()
