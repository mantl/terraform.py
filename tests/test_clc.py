# -*- coding: utf-8 -*-
import pytest


@pytest.fixture
def clc_server():
    from terraform import clc_server
    return clc_server


@pytest.fixture
def clc_resource():
    return {
        "type": "clc_server",
        "primary": {
            "id": "CA1AF-CONTROL01",
            "attributes": {
                "cpu": "2",
                "created_date": "2016-03-07T22:12:43Z",
                "group_id": "6356051ce4734c7b8fa2f780250a35a4",
                "id": "CA1AF-CONTROL01",
                "memory_mb": "4096",
                "metadata.#": "2",
                "metadata.dc": "CA1",
                "metadata.role": "control",
                "modified_date": "2016-03-07T22:16:55Z",
                "name": "CA1AF-CONTROL01",
                "name_template": "-control",
                "password": "Green123$",
                "power_state": "started",
                "private_ip_address": "10.50.100.13",
                "source_server_id": "CENTOS-7-64-TEMPLATE",
                "storage_type": "standard",
                "type": "standard"
            }
        }
    }


def test_name(clc_resource, clc_server):
    name, _, _ = clc_server(clc_resource, '')
    assert name == 'CA1AF-CONTROL01'

@pytest.mark.parametrize('attr,should', {
    'metadata': {
        'role':'control',
        'dc': 'CA1'
    },
    'ansible_ssh_port': 22,
    'ansible_ssh_user': 'root',
    'ansible_ssh_host': '10.50.100.13',
    'private_ipv4': '10.50.100.13',
    'publicly_routable': False,
    'consul_dc': 'CA1',
    'role': 'control',
    'provider': 'clc',
}.items())
def test_attrs(clc_resource, clc_server, attr, should):
    _, attrs, _ = clc_server(clc_resource, 'CA1')
    assert attr in attrs
    assert attrs[attr] == should


@pytest.mark.parametrize('group', [
    'role=control',
    'dc=CA1'
])
def test_groups(clc_resource, clc_server, group):
    _, _, groups = clc_server(clc_resource, 'CA1')
    assert group in groups
