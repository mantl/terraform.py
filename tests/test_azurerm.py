# -*- coding: utf-8 -*-
import pytest


@pytest.fixture
def azurerm_host():
    from ati.terraform import azurerm_host
    return azurerm_host


@pytest.fixture
def azurerm_resource():
    return {
        "type": "azurerm_virtual_machine",
        "depends_on": [
            "azurerm_network_interface.nic"
        ],
        "primary": {
            "id": "/subscriptions/mysubguid/resourceGroups/terraformdemo/providers/Microsoft.Compute/virtualMachines/terraformdemo",
            "attributes": {
                "delete_data_disks_on_termination": "false",
                "delete_os_disk_on_termination": "false",
                "id": "/subscriptions/mysubguid/resourceGroups/terraformdemo/providers/Microsoft.Compute/virtualMachines/terraformdemo",
                "location": "ukwest",
                "name": "terraformdemo",
                "network_interface_ids.#": "1",
                "network_interface_ids.3454837957": "/subscriptions/mysubguid/resourceGroups/terraformdemo/providers/Microsoft.Network/networkInterfaces/terraformdemo_nic0",
                "os_profile.#": "1",
                "os_profile.3552212945.admin_password": "",
                "os_profile.3552212945.admin_username": "terraformdemoadmin",
                "os_profile.3552212945.computer_name": "terraformdemo",
                "os_profile.3552212945.custom_data": "",
                "os_profile_linux_config.#": "1",
                "os_profile_linux_config.2972667452.disable_password_authentication": "false",
                "os_profile_linux_config.2972667452.ssh_keys.#": "2",
                "os_profile_linux_config.2972667452.ssh_keys.1.key_data": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCuXxPfC3b1/ps99+b7qGUVtrW+hvqoUqc/90f9/QnUa21mnDsOtC3TYgr318az6GFXwp3fdOVQKrieAjMCJjfyAZICxrEjpSTCEOh+qRaUJxRy+Mn2DqrlMB32erNAu68Z837VSyGvkPxFrhLXZryuTBvGK6/WbI6uS4Nxpglre1EDeru/8QChjDA+RN8A06Td0MMv3TMJCf0iWaRrlDEbdvi6Ceq30iJZ655TJ4h3fHIn8oONdlJTLmqliUPgg0WvhQAZPFQWyYAzfLaEix+BvwLXJSRCm31zSTmxmYVkjHJDr4UTUKMTEhW1GlTxOqc6oRrH8d07wrCjf70v1op1\n",
                "os_profile_linux_config.2972667452.ssh_keys.1.path": "/home/terraformdemoadmin/.ssh/authorized_keys",
                "os_profile_secrets.#": "0",
                "resource_group_name": "terraformdemo",
                "storage_data_disk.#": "0",
                "storage_image_reference.#": "1",
                "storage_image_reference.1222634046.offer": "UbuntuServer",
                "storage_image_reference.1222634046.publisher": "Canonical",
                "storage_image_reference.1222634046.sku": "16.04-LTS",
                "storage_image_reference.1222634046.version": "latest",
                "storage_os_disk.#": "1",
                "storage_os_disk.2197840352.caching": "ReadWrite",
                "storage_os_disk.2197840352.create_option": "FromImage",
                "storage_os_disk.2197840352.disk_size_gb": "0",
                "storage_os_disk.2197840352.image_uri": "",
                "storage_os_disk.2197840352.name": "terraformdemo_os",
                "storage_os_disk.2197840352.os_type": "",
                "storage_os_disk.2197840352.vhd_uri": "https://terraformdemo.blob.core.windows.net/vhds/terraformdemo_disk.vhd",
                "tags.%": "5",
                "tags.environment": "terraformdemo",
                "tags.os": "ubuntu",
                "tags.role": "myrole",
                "tags.ssh_ip": "10.10.0.1",
                "tags.ssh_user": "terraformdemoadmin",
                "vm_size": "Standard_D2_v2"
            },
        },
    }


def test_name(azurerm_resource, azurerm_host):
    name, _, _ = azurerm_host(azurerm_resource, '')
    assert name == 'terraformdemo'

@pytest.mark.parametrize('attr,should', {
        "id": "/subscriptions/mysubguid/resourceGroups/terraformdemo/providers/Microsoft.Compute/virtualMachines/terraformdemo",
        "name": "terraformdemo",
        "ansible_ssh_user": "terraformdemoadmin",
        "ansible_ssh_host": "10.10.0.1",
}.items())
def test_attrs(azurerm_resource, azurerm_host, attr, should):
    _, attrs, _ = azurerm_host(azurerm_resource, 'ukwest')
    assert attr in attrs
    assert attrs[attr] == should


@pytest.mark.parametrize('group', [
        'role=myrole'
])
def test_groups(azurerm_resource, azurerm_host, group):
    _, _, groups = azurerm_host(azurerm_resource, 'ukwest')
    assert group in groups
