# -*- coding: utf-8 -*-
import pytest

@pytest.fixture
def vsphere_host():
    from terraform import vsphere_host
    return vsphere_host

@pytest.fixture
def vsphere_resource():
    return {
        "type": "vsphere_virtual_machine",
        "primary": {
            "id": "12345678",
            "attributes": {
                "custom_configuration_parameters.#": "4",
                "custom_configuration_parameters.python_bin": "/usr/bin/python",
                "custom_configuration_parameters.role": "control",
                "custom_configuration_parameters.ssh_user": "vsphere-user",
                "custom_configuration_parameters.consul_dc": "module_name",
                "disk.#": "1",
                "disk.0.datastore": "main01",
                "disk.0.iops": "0",
                "disk.0.size": "0",
                "disk.0.template": "centos7-base",
                "domain": "domain.com",
                "id": "server01",
                "memory": "2048",
                "name": "mi-control-01",
                "network_interface.#": "1",
                "network_interface.0.adapter_type": "",
                "network_interface.0.ip_address": "5.6.7.8",
                "network_interface.0.ipv4_address": "1.2.3.4",
                "network_interface.0.ipv4_prefix_length": "24",
                "network_interface.0.ipv6_address": "",
                "network_interface.0.ipv6_prefix_length": "64",
                "network_interface.0.label": "VM Network",
                "network_interface.0.subnet_mask": "",
                "time_zone": "Etc/UTC",
                "vcpu": "1"
            }
        }
    }

def test_name(vsphere_resource, vsphere_host):
    name, _, _ = vsphere_host(vsphere_resource, '')
    assert name == "mi-control-01"

@pytest.mark.parametrize('attr,should', {
    'id': 'server01',
    # ansible
    'ansible_ssh_host': '1.2.3.4',
    'ansible_ssh_port': 22,
    'ansible_ssh_user': 'vsphere-user',
    'ansible_python_interpreter': '/usr/bin/python',
    # generic
    'public_ipv4': '1.2.3.4',
    'private_ipv4': '1.2.3.4',
    'provider': 'vsphere',
    # mi
    'consul_dc': 'module_name',
    'role': 'control',
}.items())
def test_attrs(vsphere_resource, vsphere_host, attr, should):
    _, attrs, _ = vsphere_host(vsphere_resource, 'module_name')
    assert attr in attrs
    assert attrs[attr] == should
