# -*- coding: utf-8 -*-
import random

import hypothesis.strategies as st

from string import ascii_letters, ascii_lowercase, digits

aws_region_list = [
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2',
    'ap-south-1',
    'ap-northeast-1',
    'ap-northeast-2',
    'ap-southeast-1',
    'ap-southeast-2',
    'eu-central-1',
    'eu-west-1',
    'eu-west-2']

# this is preparing for more backend types
def get_be_config_st(be):
    backend_dict  = {
    's3': s3_backend_config_st}

    return backend_dict[be]

@st.composite
def lineage_st(draw):
    """Hypothesis strategy for generated lineage strings."""
    first = draw(st.text(
        alphabet = list('abcdef0123456789'),
        min_size=8,
        max_size=8))
    second = draw(st.text(
        alphabet = list('abcdef0123456789'),
        min_size=4,
        max_size=4))
    third = draw(st.text(
        alphabet = list('abcdef0123456789'),
        min_size=4,
        max_size=4))
    fourth = draw(st.text(
        alphabet = list('abcdef0123456789'),
        min_size=4,
        max_size=4))
    fifth = draw(st.text(
        alphabet = list('abcdef0123456789'),
        min_size=12,
        max_size=12))

    return '{}-{}-{}-{}-{}'.format(first, second, third, fourth, fifth)

@st.composite
def s3_bucket_name_st(draw):
    """Hypothesis strategy for s3 bucket names.
    
    http://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-s3-bucket-naming-requirements.html
    """
    char1 = draw(st.text(
        alphabet = list(ascii_lowercase + digits),
        min_size=1,
        max_size=1))
    middle = draw(st.text(
        alphabet = list(ascii_lowercase + digits + '.-'),
        min_size = 4,
        max_size = 61).filter(lambda x: '..' not in x and '.-' not in x and '.-' not in x))
    endchar = draw(st.text(
        alphabet = list(ascii_lowercase + digits + '.'),
        min_size = 1,
        max_size = 1))

    return '{}{}{}'.format(char1, middle, endchar)

@st.composite
def s3_backend_config_st(draw):
    """Hypothesis strategy for s3 backend configuration."""
    s3_be_dict = {
        'bucket': draw(s3_bucket_name_st()),
        'encrypt': draw(st.sampled_from(['true', 'false'])),
        'key': draw(st.text(
            alphabet=list(ascii_letters + digits + '!-_.*\'()/'),
            min_size=1,
            max_size=1024).filter(lambda x: x[0] not in '/')),
        'region': draw(st.sampled_from(aws_region_list)) }

    if bool(random.getrandbits(1)):
        s3_be_dict['profile'] = 'testawsprofile'
    return s3_be_dict


@st.composite
def remote_init_st(draw):
    """Hypothesis strategy to generate terraform remote init state."""
    be_type = draw(st.sampled_from(['s3']))
    ri_dict = {
        "version": 3,
        "serial": 0,
        "lineage": draw(lineage_st()),
        "backend": {
            "type": be_type,
            "config": draw(get_be_config_st(be_type)()),
            "hash": draw(st.text(alphabet=list(digits), min_size=18, max_size=18))
        },
        "modules": [
            {
                "path": [
                    "root"
                ],
                "outputs": {},
                "resources": {},
                "depends_on": []
            }
        ]
    }

    return ri_dict
