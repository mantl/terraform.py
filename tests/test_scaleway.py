# -*- coding: utf-8 -*-
import pytest


@pytest.fixture
def scaleway_host():
    from ati.terraform import scaleway_host
    return scaleway_host


@pytest.fixture
def scaleway_resource():
    return {
                    "type": "scaleway_server",
                    "depends_on": [
                        "data.scaleway_image.ubuntu"
                    ],
                    "primary": {
                        "id": "a982f5e3-5ad4-4c01-b4bf-f47a7b834e43",
                        "attributes": {
                            "enable_ipv6": "false",
                            "id": "a982f5e3-5ad4-4c01-b4bf-f47a7b834e43",
                            "image": "7258ac9b-61e7-4f69-a72d-b424de25fe84",
                            "name": "test-server-01",
                            "private_ip": "55.55.55.55",
                            "public_ip": "77.77.77.77",
                            "state": "running",
                            "state_detail": "booted",
                            "tags.#": "3",
                            "tags.0": "frontend",
                            "tags.1": "dev",
                            "tags.2": "lga",
                            "type": "VC1M",
                            "volume.#": "1",
                            "volume.0.size_in_gb": "20",
                            "volume.0.type": "l_ssd",
                            "volume.0.volume_id": "282baeb3-f87b-45cf-b423-790fd95c5ad1"
                        },
                    },
                }


def test_name(scaleway_resource, scaleway_host):
    name, _, _ = scaleway_host(scaleway_resource, '')
    assert name == 'test-server-01'


@pytest.mark.parametrize('attr,should', {
    'enable_ipv6': 'false',
    'id': 'a982f5e3-5ad4-4c01-b4bf-f47a7b834e43',
    'image': '7258ac9b-61e7-4f69-a72d-b424de25fe84',
    'name': 'test-server-01',
    'private_ip': '55.55.55.55',
    'public_ip': '77.77.77.77',
    'state': 'running',
    'state_detail': 'booted',
    'tags': ['dev', 'frontend', 'lga'],
    'type': 'VC1M',
    # ansible
    'ansible_ssh_host': '77.77.77.77',
    'ansible_ssh_user': 'root',
    # generic
    'private_ipv4': '55.55.55.55',
    'public_ipv4': '77.77.77.77',
    'provider': 'scaleway',
}.items())
def test_attrs(scaleway_resource, scaleway_host, attr, should):
    _, attrs, _ = scaleway_host(scaleway_resource, 'module_name')
    assert attr in attrs
    assert attrs[attr] == should


@pytest.mark.parametrize(
    'group',
    ['scaleway_image=7258ac9b-61e7-4f69-a72d-b424de25fe84', 'scaleway_type=VC1M', 'scaleway_state=running',
     'scaleway_tag=frontend', 'scaleway_tag=dev', 'scaleway_tag=lga'])
def test_groups(scaleway_resource, scaleway_host, group):
    _, _, groups = scaleway_host(scaleway_resource, 'module_name')
    assert group in groups
