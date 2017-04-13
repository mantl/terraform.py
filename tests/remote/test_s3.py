# -*- coding: utf-8 -*-
import os
from copy import deepcopy

import boto3
import json
import pytest

from moto import mock_s3
from hypothesis import given

from ati.errors import InvalidRemoteError
from ati.remote import s3_remote_state as s3rs
from fixtures.hypothesis_state import remote_init_st


mock_creds = """
[default]
aws_access_key_id = CTTTTTTTAKIATTTTTTRP
aws_secret_access_key = RBjcAzSD2TTTTTTx+dsTTTTTTFKj6aTTTTTTg4fd

[testawsprofile]
aws_access_key_id = AKIATTTTTTRPCTTTTTTT
aws_secret_access_key = TTTTTTFKj6aTTTTTTg4fdRBjcAzSD2TTTTTTx+ds
"""

error_raising_state = {
    "backend": {
        "type": "s3",
        "config": {
            "bucket": "test-terraform",
            "encrypt": "true",
            "key": "test-customer/terraform.tfstate",
            "profile": "testawsprofile",
            "region": "us-east-1" }}}


@pytest.fixture(scope='session')
def mockcredentials(tmpdir_factory):
    mockcredsfile = tmpdir_factory.mktemp("aws").join("credentials")
    mockcredsfile.write(mock_creds)
    return mockcredsfile


@mock_s3
@given(init_state=remote_init_st())
def test_get_remote_state(init_state, monkeypatch, mockcredentials):
    def mockcreds(path):
        return mockcredentials.strpath

    conn = boto3.client('s3', region_name='us-east-1')
    local_init_state = init_state

    bucket_name = local_init_state['backend']['config']['bucket']
    key_name = local_init_state['backend']['config']['key']

    conn.create_bucket(Bucket=bucket_name)

    monkeypatch.setattr(os.path, 'expanduser', mockcreds)
    with open('tests/fixtures/remote_state.json', 'r') as f:
        remote_state_contents = f.read()

    conn.put_object(
            Bucket=bucket_name,
            Key=key_name,
            Body=remote_state_contents)

    remote_state_dict = s3rs.get_remote_state(init_state)
    assert remote_state_dict == json.loads(remote_state_contents)


def test_missing_config_throws_invalid_remote():
    init_state = deepcopy(error_raising_state)
    init_state['backend'].pop('config')
    with pytest.raises(InvalidRemoteError):
        s3rs.verify_s3(init_state)


@pytest.mark.parametrize("missing_key", [
    "key",
    "bucket"])
def test_missing_configkey_throws_invalid_remote(missing_key):
    init_state = deepcopy(error_raising_state)
    init_state['backend']['config'].pop(missing_key)

    with pytest.raises(InvalidRemoteError):
        s3rs.verify_s3(init_state)
