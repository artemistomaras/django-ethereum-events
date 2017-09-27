from django.conf import settings
from web3 import Web3, RPCProvider

from .singleton import Singleton


class Web3Service(metaclass=Singleton):
    """Creates a `web3` instance based on the given `RPCProvider`."""

    def __init__(self, *args, **kwargs):
        """Initializes the `web3` object.

        Args:
            rpc_provider (:obj:`Provider`, optional): Valid `web3` Provider instance.
        """
        rpc_provider = kwargs.pop('rpc_provider', None)
        if not rpc_provider:
            rpc_provider = RPCProvider(
                host=settings.ETHEREUM_NODE_HOST,
                port=settings.ETHEREUM_NODE_PORT,
                ssl=settings.ETHEREUM_NODE_SSL
            )
        self.web3 = Web3(rpc_provider)
        super(Web3Service, self).__init__()
