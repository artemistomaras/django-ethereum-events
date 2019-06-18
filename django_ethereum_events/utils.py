import json

from django.core.cache import cache

from eth_utils import encode_hex, event_abi_to_log_topic

from hexbytes import HexBytes

from web3.datastructures import AttributeDict


def get_event_abi(abi, event_name):
    """Helper function that extracts the event abi from the given abi.

    Args:
        abi (list): the contract abi
        event_name (str): the event name

    Returns:
        dict: the event specific abi
    """
    for entry in abi:
        if 'name' in entry.keys() and entry['name'] == event_name and \
                entry['type'] == "event":
            return entry
    raise ValueError(
        'Event `{0}` not found in the contract abi'.format(event_name))


def event_topic_from_contract_abi(abi, event_name):
    """Returns the event topic from the contract abi.

    Args:
        abi (obj): contract abi
        event_name (str): the desired event

    Returns:
        the event topic in hexstring form
    """
    if isinstance(abi, str):
        abi = json.loads(abi)

    event_abi = get_event_abi(abi, event_name)
    event_topic = event_abi_to_log_topic(event_abi)
    return event_topic.hex()


def refresh_cache_update_value(update_required=False):
    from .models import CACHE_UPDATE_KEY
    cache.set(CACHE_UPDATE_KEY, update_required)


class Singleton(type):
    """Simple singleton implementation."""

    _instances = {}

    def __call__(cls, *args, **kwargs):  # noqa: N805
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class HexJsonEncoder(json.JSONEncoder):
    """JSONEncoder that parses decoded logs as returned from `web3.utils.events.get_event_data`."""

    def default(self, obj):
        if isinstance(obj, HexBytes):
            return obj.hex()
        elif isinstance(obj, AttributeDict):
            return dict(obj)
        elif isinstance(obj, bytes):
            return encode_hex(obj)
        return super().default(obj)
