# -*- coding: utf-8 -*-
import boto3
import json
from moto import mock_s3

from ati.remote import s3_remote_state as s3rs

@mock_s3
def test_get_remote_state():
    conn = boto3.resource('s3', region_name='us-east-1')
    conn.create_bucket(Bucket='terraform')
    # nothing happening yet

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
