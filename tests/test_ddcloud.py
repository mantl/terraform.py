# -*- coding: utf-8 -*-
import pytest


@pytest.fixture
def ddcloud_server():
    from ati.terraform import ddcloud_server
    return ddcloud_server


@pytest.fixture
def ddcloud_resource():
    return {
        'type': 'ddcloud_server',
        'primary': {
            'id': '548dedab-9455-4f54-a683-f3a01018dfcd',
            'attributes': {
                'admin_password': 'sn4uSag3s!',
                'auto_start': 'true',
                'cpu_count': '4',
                'description': 'Edge node 1 for au9 cluster.',
                'disk.#': '3',
                'disk.1616808471.disk_id': '9bf46fb7-e0bf-430e-9872-cad92cd2ac3e',
                'disk.1616808471.scsi_unit_id': '1',
                'disk.1616808471.size_gb': '50',
                'disk.1616808471.speed': 'STANDARD',
                'disk.219226128.disk_id': '500b7ecb-1f5e-4aae-b7b3-53175da79423',
                'disk.219226128.scsi_unit_id': '0',
                'disk.219226128.size_gb': '10',
                'disk.219226128.speed': 'STANDARD',
                'disk.3717523161.disk_id': '04ee5a84-264c-45aa-b692-d6c111d8a80d',
                'disk.3717523161.scsi_unit_id': '2',
                'disk.3717523161.size_gb': '50',
                'disk.3717523161.speed': 'STANDARD',
                'dns_primary': '8.8.8.8',
                'dns_secondary': '8.8.4.4',
                'id': '548dedab-9455-4f54-a683-f3a01018dfcd',
                'memory_gb': '6',
                'name': 'au9-edge-01',
                'networkdomain': 'de1a94a3-69ba-4f53-a4e6-df26282bb09d',
                'os_image_id': 'e1b4e0cc-35ba-47be-a2d7-1b5601b87119',
                'os_image_name': 'CentOS 7 64-bit 2 CPU',
                'primary_adapter_ipv4': '10.5.50.25',
                'primary_adapter_ipv6': '2402:9900:111:1376:44f9:4cb4:cc32:4c8e',
                'primary_adapter_vlan': 'afeb4035-9da4-4681-90bd-e2bc370dd942',
                'public_ipv4': '168.128.37.189',
                'tag.#': '2',
                'tag.441773823.name': 'consul_dc',
                'tag.441773823.value': 'au9',
                'tag.676038111.name': 'role',
                'tag.676038111.value': 'edge'
            }
        }
    }


def test_name(ddcloud_resource, ddcloud_server):
    name, _, _ = ddcloud_server(ddcloud_resource, '')
    assert name == 'au9-edge-01'


@pytest.mark.parametrize('attr,should', {
    'id': '548dedab-9455-4f54-a683-f3a01018dfcd',
    'role': 'edge',
    'consul_dc': 'au9',
    
    'network_domain': 'de1a94a3-69ba-4f53-a4e6-df26282bb09d',
    
    'image_type': 'os',
    'image_id': 'e1b4e0cc-35ba-47be-a2d7-1b5601b87119',
    'image_name': 'CentOS 7 64-bit 2 CPU',
    
    'ansible_ssh_host': '168.128.37.189',
    'ansible_ssh_user': 'root',

    'private_ipv4': '10.5.50.25',
    'public_ipv4': '168.128.37.189',

    'primary_ipv6': '2402:9900:111:1376:44f9:4cb4:cc32:4c8e'
}.items())
def test_attrs(ddcloud_resource, ddcloud_server, attr, should):
    _, attrs, _ = ddcloud_server(ddcloud_resource, 'module_name')
    assert attr in attrs
    assert attrs[attr] == should


@pytest.mark.parametrize('group', [
    'role=edge',
    'dc=au9',
])
def test_groups(ddcloud_resource, ddcloud_server, group):
    _, _, groups = ddcloud_server(ddcloud_resource, 'module_name')
    assert group in groups
