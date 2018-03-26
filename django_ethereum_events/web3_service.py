from django.conf import settings
from django.utils.six import with_metaclass

from web3 import Web3

try:
    from web3 import HTTPProvider
    RPCProvider = None
except ImportError:
    from web3 import RPCProvider
    HTTPProvider = None

from .singleton import Singleton


class Web3Service(with_metaclass(Singleton)):
    """Creates a `web3` instance based on the given `RPCProvider`."""

    def __init__(self, *args, **kwargs):
        """Initializes the `web3` object.

        Args:
            rpc_provider (:obj:`Provider`, optional): Valid `web3` Provider
                instance.
        """
        rpc_provider = kwargs.pop('rpc_provider', None)
        if not rpc_provider:
            timeout = getattr(settings, "ETHEREUM_NODE_TIMEOUT", 10)
            if HTTPProvider is not None:
                uri = "{scheme}://{host}:{port}".format(
                    host=settings.ETHEREUM_NODE_HOST,
                    port=settings.ETHEREUM_NODE_PORT,
                    scheme="https" if settings.ETHEREUM_NODE_SSL else "http",
                )
                rpc_provider = HTTPProvider(
                    endpoint_uri=uri,
                    request_kwargs={
                        "timeout": timeout
                    }
                )
            elif RPCProvider is not None:
                rpc_provider = RPCProvider(
                    host=settings.ETHEREUM_NODE_HOST,
                    port=settings.ETHEREUM_NODE_PORT,
                    ssl=settings.ETHEREUM_NODE_SSL,
                    timeout=timeout
                )
            else:
                raise ValueError("Cannot instantiate any RPC provider")
        self.web3 = Web3(rpc_provider)
        super(Web3Service, self).__init__()
