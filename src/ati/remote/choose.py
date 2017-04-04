from ati.errors import InvalidRemoteError

from ati.remote import s3_remote_state


def _verify_s3(state : dict):
    """ verify this state init s3 remote state

    Args:
        state: local state file

    Returns:
        func: the function to fetch remote state from s3, or None if no
        remote state

    """
    if 'config' not in state['backend']:
        raise InvalidRemoteError((
            'Your remote state configuration does not have a config section '
            'and is thus invalid.'))
    if 'key' not in state['backend']['config']:
        raise InvalidRemoteError((
            'Your s3 remote state configuration does not have a state file key '
            'and is thus invalid.'))
    if 'bucket' not in state['backend']['config']:
        raise InvalidRemoteError((
            'Your s3 remote state configuration does not have a bucket and is'
            ' thus invalid.'))
    # if all these checks pass without returning, it's s3 remote state
    return s3_remote_state.get_remote_state


verifiers = {
    's3': _verify_s3}


def get_remote_func(state : dict):
    """ choose which function to use for remote state

    Args:
        state: local state file

    Returns:
        func: the function to be used to fetch the remote state, or None if
            no remote state

    """
    if not 'backend' in state:
        return None
    if not 'type' in state['backend']:
        return None
    if state['backend']['type'] in verifiers:
        return verifiers[state['backend']['type']](state)

    return None
