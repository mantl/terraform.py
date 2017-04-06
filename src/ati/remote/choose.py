# -*- coding: utf-8 -*-
from ati.remote.s3_remote_state import verify_s3

verifiers = {
    's3': verify_s3}


def get_remote_func(state : dict):
    """ Choose which function to use for remote state.

    Args:
        state: local state file

    Returns:
        func: the function to be used to fetch the remote state, or None if
            no remote state

    """
    try:
        verify_fn = verifiers[state['backend']['type']]
    except KeyError:
        return None

    return verify_fn(state)
