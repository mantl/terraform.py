# -*- coding: utf-8 -*-
import pytest


@pytest.fixture
def digitalocean_host():
    from terraform import digitalocean_host
    return digitalocean_host


@pytest.fixture
def digitalocean_resource():
    return {
        "type": "digitalocean_droplet",
        "primary": {
            "id": "5726884", "attributes": {
                "id": "5726884", "image": "centos-7-0-x64", "ipv4_address":
                "1.2.3.4", "locked": "false", "name": "mi-control-01", "region":
                "nyc3", "size": "4gb", "ssh_keys.#": "1", "ssh_keys.0":
                "895599", "status": "active", "user_data": '{"role":"control"}'
            }
        }
    }


def test_name(digitalocean_resource, digitalocean_host):
    name, _, _ = digitalocean_host(digitalocean_resource, '')
    assert name == 'mi-control-01'


@pytest.mark.parametrize('attr,should', {
    'id': '5726884',
    'image': 'centos-7-0-x64',
    'ipv4_address': '1.2.3.4',
    'locked': False,
    'metadata': {'role': 'control'},
    'region': 'nyc3',
    'size': '4gb',
    'ssh_keys': ['895599'],
    'status': 'active',
    # ansible
    'ansible_ssh_host': '1.2.3.4',
    'ansible_ssh_port': 22,
    'ansible_ssh_user': 'root',
    # generic
    'public_ipv4': '1.2.3.4',
    'private_ipv4': '1.2.3.4',
    'provider': 'digitalocean',
    # mi
    'consul_dc': 'nyc3',
    'role': 'control',
}.items())
def test_attrs(digitalocean_resource, digitalocean_host, attr, should):
    _, attrs, _ = digitalocean_host(digitalocean_resource, 'module_name')
    assert attr in attrs
    assert attrs[attr] == should


@pytest.mark.parametrize(
    'group', ['do_image=centos-7-0-x64', 'do_locked=False', 'do_region=nyc3',
              'do_size=4gb', 'do_status=active', 'do_metadata_role=control',
              'role=control', 'dc=nyc3']
)
def test_groups(digitalocean_resource, digitalocean_host, group):
    _, _, groups = digitalocean_host(digitalocean_resource, 'module_name')
    assert group in groups
