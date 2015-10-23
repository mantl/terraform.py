# -*- coding: utf-8 -*-
import pytest


@pytest.fixture
def azure_host():
    from terraform import azure_host
    return azure_host


@pytest.fixture
def azure_resource():
    return {
        "type": "azure_instance",
        "depends_on": [
            "azure_hosted_service.mesos-master",
            "azure_security_group.default",
            "azure_storage_service.azure_mesos_storage",
            "azure_storage_service.azure_mesos_storage",
            "azure_virtual_network.public"
        ],
        "primary": {
            "id": "mi-control-01",
            "attributes": {
                "automatic_updates": "false",
                "description": "mesos_masters",
                "endpoint.#": "9",
                "endpoint.2462817782.name": "SSH",
                "endpoint.2462817782.private_port": "22",
                "endpoint.2462817782.protocol": "tcp",
                "endpoint.2462817782.public_port": "22",
                "hosted_service_name": "hosted-service-name-mi-control-01",
                "id": "mi-control-01",
                "image": "apollo-ubuntu-14.04-amd64-1444419199",
                "ip_address": "10.0.0.5",
                "location": "North Europe",
                "name": "mi-control-01",
                "reverse_dns": "",
                "security_group": "default-apollo-mesos",
                "size": "Medium",
                "ssh_key_thumbprint": "156E660861DBED413BE0F9E617FF7D720E019943",
                "storage_service_name": "mesosimages",
                "subnet": "public-network-subnet",
                "username": "ubuntu",
                "vip_address": "137.135.187.208",
                "virtual_network": "public-network"
            }
        }
    }


def test_name(azure_resource, azure_host):
    name, _, _ = azure_host(azure_resource, '')
    assert name == 'mi-control-01'

@pytest.mark.parametrize('attr,should', {
    'username': 'ubuntu',
    'automatic_updates': 'false',
    'description': 'mesos_masters',
    'image': 'apollo-ubuntu-14.04-amd64-1444419199',
    'ssh_key_thumbprint': '156E660861DBED413BE0F9E617FF7D720E019943',
    'consul_dc': 'north-europe',
    'ansible_ssh_port': 22,
    'ip_address': '10.0.0.5',
    'id': 'mi-control-01',
    'size': 'Medium',
    'subnet': 'public-network-subnet',
    "endpoint": [
        {
            'private_port': '22',
            'public_port': '22',
            'protocol': 'tcp',
            'name': 'SSH'
        }
    ],
    'name': 'mi-control-01',
    'hosted_service_name': 'hosted-service-name-mi-control-01',
    'ansible_ssh_host': '137.135.187.208',
    'reverse_dns': '',
    'ansible_ssh_user': 'ubuntu',
    'role': 'mesos_masters',
    'location': 'North Europe',
    'vip_address': '137.135.187.208',
    'security_group': 'default-apollo-mesos',
    'virtual_network': 'public-network',
    'consul_is_server': False
}.items())
def test_attrs(azure_resource, azure_host, attr, should):
    _, attrs, _ = azure_host(azure_resource, 'North_Europe')
    assert attr in attrs
    assert attrs[attr] == should


@pytest.mark.parametrize('group', [
    'azure_username=ubuntu',
    'dc=north-europe',
    'azure_location=north-europe',
    'azure_image=apollo-ubuntu-14.04-amd64-1444419199',
    'role=mesos_masters',
    'azure_security_group=default-apollo-mesos',
    'role=mesos_masters'
])
def test_groups(azure_resource, azure_host, group):
    _, _, groups = azure_host(azure_resource, 'North_Europe')
    assert group in groups
