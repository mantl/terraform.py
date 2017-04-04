# -*- coding: utf-8 -*-
import os

import boto3
import json
import pytest

from moto import mock_s3

from ati.remote import s3_remote_state as s3rs


mock_creds = """
[testawsprofile]
aws_access_key_id = AKIATTTTTTRPCTTTTTTT
aws_secret_access_key = TTTTTTFKj6aTTTTTTg4fdRBjcAzSD2TTTTTTx+ds
"""

@pytest.fixture(scope='session')
def mockcredentials(tmpdir_factory):
    mockcredsfile = tmpdir_factory.mktemp("aws").join("credentials")
    mockcredsfile.write(mock_creds)
    return mockcredsfile


@mock_s3
def test_get_remote_state(monkeypatch, mockcredentials):
    def mockcreds(path):
        return mockcredentials.strpath

    conn = boto3.client('s3', region_name='us-east-1')
    with open('tests/fixtures/remote_init.json', 'r') as f:
        local_init_state = json.load(f)

    bucket_name = local_init_state['backend']['config']['bucket']
    key_name = local_init_state['backend']['config']['key']
    profile_name = local_init_state['backend']['config']['profile']

    conn.create_bucket(Bucket=bucket_name)

    monkeypatch.setattr(os.path, 'expanduser', mockcreds)
    with open('tests/fixtures/remote_state.json', 'r') as f:
        remote_state_contents = f.read()

    conn.put_object(
            Bucket=bucket_name,
            Key=key_name,
            Body=remote_state_contents)



    remote_state_dict = s3rs.get_remote_state(bucket_name, key_name, profile_name)
    assert remote_state_dict == json.loads(remote_state_contents)
    


def test_is_remote_state():
    tf = None
    with open('tests/fixtures/remote_init.json', 'r') as f:
        tf = json.load(f)

    assert s3rs.is_remote_state(tf)

def test_not_remote_state():
    tf = None
    with open('tests/fixtures/local_init.json', 'r') as f:
        tf = json.load(f)

    assert not s3rs.is_remote_state(tf)
