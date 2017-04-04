# -*- coding: utf-8 -*-
import boto3
import json

from ati.errors import WrongRemoteError, InvalidRemoteError


def get_remote_state(
        bucket_name : str,
        key_name : str = 'terraform.tfstate',
        profile_name : str = 'default') -> dict:
    """ fetch remote state from s3 and return it as a dictionary

    This function is used to fetch a state file from AWS S3, convert
    and return it as a dictionary.

    Args:
        state_file: The name of the statefile in the bucket
    """
    aws_session = boto3.Session(profile_name=profile_name)
    s3 = aws_session.client('s3')

    rs_obj = s3.get_object(Bucket=bucket_name, Key=key_name)
    
    return json.loads(rs_obj['Body'].read().decode('utf-8'))



def is_remote_state(tfstate : dict) -> bool:
    """ determine if this state file means that remote state is available

    Args:
        tfstate: A terraform state dictionary (tfstate, already parsed)
    """
    if not 'backend' in tfstate:
        return False
    if not 'type' in tfstate['backend']:
        return False
    if tfstate['backend']['type'] != 's3':
        raise WrongRemoteError((
            'The given terraform state file has a backend type of {}, '
            'not s3').format(tfstate['backend']['type']))
    if 'config' not in tfstate['backend']:
        raise InvalidRemoteError((
            'Your remote state configuration does not have a config section '
            'and is thus invalid.'))
    if 'key' not in tfstate['backend']['config']:
        raise InvalidRemoteError((
            'Your remote state configuration does not have a state file key '
            'and is thus invalid.'))
    if 'bucket' not in tfstate['backend']['config']:
        raise InvalidRemoteError((
            'Your remote state configuration does not have a bucket and is'
            ' thus invalid.'))
    # if all these checks pass without returning, it's s3 remote state
    return True
