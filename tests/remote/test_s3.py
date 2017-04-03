from moto import mock_s3

import boto3  # noqa

@mock_s3
def test_get_remote_state():
    conn = boto3.resource('s3', region_name='us-east-1')
    conn.create_bucket(Bucket='terraform')
