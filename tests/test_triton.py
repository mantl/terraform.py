# -*- coding: utf-8 -*-
import pytest


@pytest.fixture
def triton_machine():
    from terraform import triton_machine
    return triton_machine


@pytest.fixture
def triton_resource():
    return {
        "type": "triton_machine",
        "primary": {
            "id": "69818186-01ed-4f5b-af1b-ce9c23e16f82",
            "attributes": {
                "administrator_pw": "",
                "created": "2016-04-27T18:57:49.189Z",
                "dataset": "",
                "disk": "122880",
                "firewall_enabled": "false",
                "id": "69818186-01ed-4f5b-af1b-ce9c23e16f82",
                "image": "dd31507e-031e-11e6-be8a-8f2707b5b3ee",
                "ips.#": "2",
                "ips.0": "165.225.136.36",
                "ips.1": "10.112.7.149",
                "memory": "4096",
                "name": "mantl-control-01",
                "networks.#": "2",
                "networks.0": "65ae3604-7c5c-4255-9c9f-6248e5d78900",
                "networks.1": "56f0fd52-4df1-49bd-af0c-81c717ea8bce",
                "package": "Medium 4GB",
                "primaryip": "165.225.136.36",
                "root_authorized_keys": "key text replaced for test",
                "state": "running",
                "tags.#": "1",
                "tags.role": "control",
                "type": "virtualmachine",
                "updated": "2016-04-27T18:58:05.000Z",
                "user_data": "",
                "user_script": ""
            }
        }
    }


def test_name(triton_resource, triton_machine):
    name, _, _ = triton_machine(triton_resource, '')
    assert name == 'mantl-control-01'


@pytest.mark.parametrize('attr,should', {
    'id': '69818186-01ed-4f5b-af1b-ce9c23e16f82',
    'dataset': '',
    'disk': '122880',
    'firewall_enabled': False,
    'image': 'dd31507e-031e-11e6-be8a-8f2707b5b3ee',
    'ips': ['10.112.7.149', '165.225.136.36'],
    'name': 'mantl-control-01',
    'networks': ['56f0fd52-4df1-49bd-af0c-81c717ea8bce', '65ae3604-7c5c-4255-9c9f-6248e5d78900'],
    'package': 'Medium 4GB',
    'primary_ip': '165.225.136.36',
    'root_authorized_keys': 'key text replaced for test',
    'state': 'running',
    'tags': {'role': 'control'},
    'type': 'virtualmachine',
    'user_data': '',
    'user_script': '',
    # ansible
    'ansible_ssh_host': '165.225.136.36',
    'ansible_ssh_port': 22,
    'ansible_ssh_user': 'root',
    # generic
    'public_ipv4': '165.225.136.36',
    'private_ipv4': '10.112.7.149',
    'provider': 'triton',
    # mi
    'consul_dc': 'none',
    'role': 'control',
}.items())
def test_attrs(triton_resource, triton_machine, attr, should):
    _, attrs, _ = triton_machine(triton_resource, 'module_name')
    assert attr in attrs
    assert attrs[attr] == should


@pytest.mark.parametrize(
    'group', ['triton_image=dd31507e-031e-11e6-be8a-8f2707b5b3ee',
              'triton_package=Medium 4GB', 'triton_state=running',
              'triton_firewall_enabled=False', 'triton_tags_role=control',
              'triton_network=56f0fd52-4df1-49bd-af0c-81c717ea8bce',
              'triton_network=65ae3604-7c5c-4255-9c9f-6248e5d78900',
              'role=control', 'dc=none'],
)
def test_groups(triton_resource, triton_machine, group):
    _, _, groups = triton_machine(triton_resource, 'module_name')
    print groups
    assert group in groups
