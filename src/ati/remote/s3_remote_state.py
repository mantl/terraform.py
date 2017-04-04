# -*- coding: utf-8 -*-
import boto3
import json

from ati.errors import InvalidRemoteError


def get_remote_state(local_state : dict ) -> dict:
    """ fetch remote state from s3 and return it as a dictionary

    This function is used to fetch a state file from AWS S3, convert
    and return it as a dictionary.

    Args:
        local_state: local state file with remote information
    """
    try:
        bucket_name = local_state['backend']['config']['bucket']
        key_name = local_state['backend']['config']['key']
    except KeyError as e:
        raise InvalidRemoteError((
            'state file given to s3.get_remote_state '
            'was missing a key: {}'.format(e.msg)))

    if 'profile' in local_state['backend']['config']:
        profile_name = local_state['backend']['config']['profile']
    else:
        profile_name = 'default'

    aws_session = boto3.Session(profile_name=profile_name)
    s3 = aws_session.client('s3')

    rs_obj = s3.get_object(Bucket=bucket_name, Key=key_name)
    
    return json.loads(rs_obj['Body'].read().decode('utf-8'))


