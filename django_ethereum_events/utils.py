import json

from eth_utils import event_abi_to_log_topic


def get_event_abi(abi, event_name):
    """Helper function that extracts the event abi from the given abi.

    Args:
        abi (dict): the contract abi
        event_name (str): the event name

    Returns:
        dict: the event specific abi
    """
    for entry in abi:
        if 'name' in entry.keys() and entry['name'] == event_name and \
                entry['type'] == "event":
            return entry
    raise ValueError(
        'Event `{}` not found in the contract abi'.format(event_name))


def event_topic_from_contract_abi(abi, event_name):
    if isinstance(abi, str):
        abi = json.loads(abi)

    event_abi = get_event_abi(abi, event_name)
    event_topic = event_abi_to_log_topic(event_abi)
    return event_topic.hex()


def post_process_decoded_log(decoded_log):
    """Converts the `AttrDict` to `dict` and the `HexBytes` to `str`

    Args:
        decoded_log (AttrDict): the decoded log

    Returns:
        dict: the post processed log
    """
    mutable_decoded_log = dict(decoded_log)
    mutable_decoded_log['transactionHash'] = mutable_decoded_log['transactionHash'].hex()
    mutable_decoded_log['blockHash'] = mutable_decoded_log['blockHash'].hex()
    return mutable_decoded_log