# -*- coding: utf-8 -*-
import pytest


@pytest.fixture
def packet_device():
    from ati.terraform import packet_device
    return packet_device


@pytest.fixture
def packet_resource():
    return {
        "type": "packet_device",
        "depends_on": [
            "packet_project.workstation"
        ],
        "primary": {
            "id": "774a8d59-932b-4ba8-9685-0f4237422be5",
            "attributes": {
                "billing_cycle": "hourly",
                "created": "2016-12-11T14:55:04Z",
                "facility": "ams1",
                "hostname": "workstation",
                "id": "774a8d59-932b-4ba8-9685-0f4237422be5",
                "locked": "false",
                "network.#": "3",
                "network.0.address": "147.75.100.215",
                "network.0.cidr": "31",
                "network.0.family": "4",
                "network.0.gateway": "147.75.100.214",
                "network.0.public": "true",
                "network.1.address": "2604:1380:2000:2c00::1",
                "network.1.cidr": "127",
                "network.1.family": "6",
                "network.1.gateway": "2604:1380:2000:2c00::",
                "network.1.public": "true",
                "network.2.address": "10.80.25.129",
                "network.2.cidr": "31",
                "network.2.family": "4",
                "network.2.gateway": "10.80.25.128",
                "network.2.public": "false",
                "operating_system": "centos_7",
                "plan": "baremetal_0",
                "project_id": "573b1856-b214-43fb-9282-314d57e99eb7",
                "state": "active",
                "tags.#": "0",
                "updated": "2016-12-12T02:40:19Z",
                "user_data": "{\"dc\":\"ams1\",\"role\":\"workstation\"}"
            },
            "meta": {},
            "tainted": False
        },
        "deposed": [],
        "provider": ""
    }


def test_name(packet_resource, packet_device):
    name, _, _ = packet_device(packet_resource, '')
    assert name == '774a8d59-932b-4ba8-9685-0f4237422be5'


@pytest.mark.parametrize('attr,should', {
    'id': "774a8d59-932b-4ba8-9685-0f4237422be5",
    'facility': "ams1",
    'hostname': "workstation",
    'operating_system': "centos_7",
    'locked': False,
    'metadata': {'role': "workstation", 'dc': "ams1"},
    'plan': "baremetal_0",
    'project_id': "573b1856-b214-43fb-9282-314d57e99eb7",
    'state': 'active',
    'ansible_ssh_host': "147.75.100.215",
    'ansible_ssh_user': 'root',
    'ipv4_address': "147.75.100.215",
    'public_ipv4': "147.75.100.215",
    'ipv6_address': "2604:1380:2000:2c00::1",
    'public_ipv6': "2604:1380:2000:2c00::1",
    'private_ipv4': "10.80.25.129",
    'provider': 'packet',
    'consul_dc': 'ams1',
    'role': 'workstation',
}.items())
def test_attrs(packet_resource, packet_device, attr, should):
    _, attrs, _ = packet_device(packet_resource, 'module_name')
    assert attr in attrs
    assert attrs[attr] == should


@pytest.mark.parametrize(
    'group', ['packet_operating_system=centos_7',
              'packet_locked=False',
              'packet_facility=ams1',
              'packet_plan=baremetal_0',
              'packet_state=active',
              'packet_metadata_role=workstation',
              'role=workstation',
              'dc=ams1']
)
def test_groups(packet_resource, packet_device, group):
    _, _, groups = packet_device(packet_resource, 'module_name')
    assert group in groups
