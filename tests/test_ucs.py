# -*- coding: utf-8 -*-
import pytest


@pytest.fixture
def ucs_host():
    from terraform import ucs_host
    return ucs_host


@pytest.fixture
def ucs_resource():
    return {
        "type": "ucs_service_profile",
        "primary": {
            "id": "control-0.mydomain.com",
            "attributes": {
                "dn": "org-root/ls-control-0.mydomain.com",
		"id": "control-0.mydomain.com",
		"metadata.#": "1",
		"metadata.role": "control",
		"name": "control-0.mydomain.com",
                "service_profile_template": "CentOS",
                "target_org": "org-root",
                "vNIC.#": "1",
                "vNIC.0.cidr": "10.30.0.150/24",
                "vNIC.0.ip": "10.30.0.172",
                "vNIC.0.mac": "00:25:B5:00:0A:08",
                "vNIC.0.name": "eth0"
            },
            "meta": {"schema_version": "1"}
        }
    }


def test_name(ucs_resource, ucs_host):
    name, _, _ = ucs_host(ucs_resource, '')
    assert name == 'control-0.mydomain.com'


@pytest.mark.parametrize('attr,should', {
    'ansible_ssh_host': '10.30.0.172',
    'role': 'control',
    'consul_dc': 'root',
    'provider': 'ucs',
    'public_ipv4': '10.30.0.172',
    'private_ipv4': '10.30.0.172',
    'consul_is_server': True,
    'metadata':
    {'role': 'control', },
}.items())
def test_attrs(ucs_resource, ucs_host, attr, should):
    _, attrs, _ = ucs_host(ucs_resource, 'root')
    assert attr in attrs
    assert attrs[attr] == should

@pytest.mark.parametrize('group', [
    'role=control',
    'dc=root',
])
def test_groups(ucs_resource, ucs_host, group):
    _, _, groups = ucs_host(ucs_resource, 'root')
    assert group in groups
