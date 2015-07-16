# -*- coding: utf-8 -*-
import pytest

@pytest.fixture
def softlayer_host():
    from terraform import softlayer_host
    return softlayer_host

@pytest.fixture
def softlayer_resource():
    return {
        "type": "softlayer_virtualserver",
        "primary": {
            "id": "12345678",
            "attributes": {
                "cpu": 1,
                "domain": "example.com",
                "id": "12345678",
                "image": "CENTOS_7_64",
                "ipv4_address": "1.2.3.4",
                "ipv4_address_private": "5.6.7.8",
                "name": "mi-control-01",
                "public_network_speed": "1000",
                "ram": "4096",
                "region": "ams01",
                "ssh_keys.#": "1",
                "ssh_keys.0": "23456",
                "user_data": "{\"role\":\"control\",\"dc\":\"mi\"}"
            }
        }
    }

def test_name(softlayer_resource, softlayer_host):
    name, _, _ = softlayer_host(softlayer_resource, '')
    assert name == "mi-control-01"

@pytest.mark.parametrize('attr,should', {
    'id': '12345678',
    'image': 'CENTOS_7_64',
    'ipv4_address': '1.2.3.4',
    'metadata': {'role': 'control', 'dc': 'mi'},
    'region': 'ams01',
    'ram': '4096',
    'cpu': 1,
    'ssh_keys': ['23456'],
    # ansible
    'ansible_ssh_host': '1.2.3.4',
    'ansible_ssh_port': 22,
    'ansible_ssh_user': 'root',
    # generic
    'public_ipv4': '1.2.3.4',
    'private_ipv4': '5.6.7.8',
    'provider': 'softlayer',
    # mi
    'consul_dc': 'mi',
    'role': 'control',
}.items())
def test_attrs(softlayer_resource, softlayer_host, attr, should):
    _, attrs, _ = softlayer_host(softlayer_resource, 'module_name')
    assert attr in attrs
    assert attrs[attr] == should


@pytest.mark.parametrize(
    'group', ['dc=mi', 'role=control']
)
def test_groups(softlayer_resource, softlayer_host, group):
    _, _, groups = softlayer_host(softlayer_resource, 'module_name')
    assert group in groups
