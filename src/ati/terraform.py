# -*- coding: utf-8 -*-
#
# Copyright 2015 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""\
Dynamic inventory for Terraform - finds all `.tfstate` files below the working
directory and generates an inventory based on them.
"""

from collections import defaultdict
from functools import wraps
import json
import os
import re

import sh

# https://github.com/mantl/terraform.py/issues/74
try:
    unicode
    STRING_TYPES = [unicode, str]
except NameError:
    STRING_TYPES = [str]


def tfstates(root=None):
    root = root or os.getcwd()
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if os.path.splitext(name)[-1] == '.tfstate':
                yield os.path.join(dirpath, name)

def iter_states(root=None):
    root = root or os.getcwd()
    curdir = os.getcwd()
    for dpath, dnames, fnames in os.walk(root):
        if '.terraform' in dnames:
            try:
                os.chdir(dpath)
                output = sh.terraform("state", "pull").stdout.decode('utf-8')
                start_index = output.find('{')
                if start_index < 0:
                    start_index = 0
                yield json.loads(output[start_index:])
            finally:
                os.chdir(curdir)


def iterresources(sources):
    for source in sources:
        if type(source) in STRING_TYPES:
            with open(source, 'r') as json_file:
                state = json.load(json_file)
        else:
            state = source
        for module in state['modules']:
            name = module['path'][-1]
            for key, resource in list(module['resources'].items()):
                yield name, key, resource


def get_stage_root(tf_dirname=None, root=None):
    """Look for a terraform root directory to match the inventory root directory.

    This function is meant to aid with using separate tfstate files and separate
    ansible inventory files for different stages/environments. The idea
    is that the ansible inventory directory and the terraform state directory
    names will match. The directory of the ansible inventory call is used to find
    ONLY the terraform state with the same name as the inventory.

    Args:
        tf_dirname (str): Subdirectory name that terraform files live under.
        root (str): Root directory from which to search for terraform files.

    """
    root = root or os.getcwd()
    ansible_dir = os.getcwd()
    tf_dirname = tf_dirname or 'terraform'
    inv_name = root.split(os.path.sep)[-1]
    try:
        terraform_base = os.path.join(ansible_dir, tf_dirname)
        if inv_name in os.listdir(terraform_base):
            return os.path.join(terraform_base, inv_name)
        else:
            return root
    except OSError:
        return root


## READ RESOURCES
PARSERS = {}


def _clean_dc(dcname):
    # Consul DCs are strictly alphanumeric with underscores and hyphens -
    # ensure that the consul_dc attribute meets these requirements.
    return re.sub('[^\w_\-]', '-', dcname)


def iterhosts(resources, args):
    '''yield host tuples of (name, attributes, groups)'''
    for module_name, key, resource in resources:
        resource_type, name = key.split('.', 1)
        try:
            parser = PARSERS[resource_type]
        except KeyError:
            continue

        yield parser(resource, module_name, args=args)


def parses(prefix):
    def inner(func):
        PARSERS[prefix] = func
        return func

    return inner


def calculate_mantl_vars(func):
    """calculate Mantl vars"""

    @wraps(func)
    def inner(*args, **kwargs):
        name, attrs, groups = func(*args, **kwargs)

        # attrs
        if attrs.get('role', '') == 'control':
            attrs['consul_is_server'] = True
        else:
            attrs['consul_is_server'] = False

        # groups
        if attrs.get('publicly_routable', False):
            groups.append('publicly_routable')

        return name, attrs, groups

    return inner


def _parse_prefix(source, prefix, sep='.'):
    for compkey, value in list(source.items()):
        try:
            curprefix, rest = compkey.split(sep, 1)
        except ValueError:
            continue

        if curprefix != prefix or rest == '#':
            continue

        yield rest, value


def parse_attr_list(source, prefix, sep='.'):
    attrs = defaultdict(dict)
    for compkey, value in _parse_prefix(source, prefix, sep):
        idx, key = compkey.split(sep, 1)
        attrs[idx][key] = value

    return list(attrs.values())


def parse_dict(source, prefix, sep='.'):
    return dict(_parse_prefix(source, prefix, sep))


def parse_list(source, prefix, sep='.'):
    return [value for _, value in _parse_prefix(source, prefix, sep)]


def parse_bool(string_form):
    token = string_form.lower()[0]

    if token == 't':
        return True
    elif token == 'f':
        return False
    else:
        raise ValueError('could not convert %r to a bool' % string_form)


@parses('ddcloud_server')
@calculate_mantl_vars
def ddcloud_server(resource, module_name):
    raw_attrs = resource['primary']['attributes']
    name = raw_attrs.get('name')
    groups = []

    tags = {}
    raw_tags = parse_attr_list(raw_attrs, 'tag')
    for raw_tag in raw_tags:
        tags[raw_tag['name']] = raw_tag['value']

    attrs = {
        'id': raw_attrs['id'],
        'name': raw_attrs['name'],
        'primary_ip': raw_attrs['public_ipv4'], # not available immediately after creation; you'll need to run terraform refresh first.
        'tags': tags,

        'network_domain': raw_attrs['networkdomain'],

        # ansible
        'ansible_ssh_host': raw_attrs['public_ipv4'],
        'ansible_ssh_user': 'root',  # it's always "root" on CloudControl images

        # generic
        'private_ipv4': raw_attrs['primary_adapter_ipv4'],
        'public_ipv4': raw_attrs['public_ipv4'],
        'primary_ipv6': raw_attrs['primary_adapter_ipv6'],

        'provider': 'ddcloud',
    }

    # image details
    if 'os_image_id' in raw_attrs:
        attrs['image_type'] = 'os'
        attrs['image_id'] = raw_attrs['os_image_id']
        attrs['image_name'] = raw_attrs['os_image_name']
    else:
        attrs['image_type'] = 'customer'
        attrs['image_id'] = raw_attrs['customer_image_id']
        attrs['image_name'] = raw_attrs['customer_image_name']

    # attrs specific to Mantl
    attrs.update({
        'role': tags.get('role', 'none'),
        'consul_dc': _clean_dc(tags.get('consul_dc', 'none'))
    })

    # groups specific to Mantl
    groups.append('role=' + attrs['role'])
    groups.append('dc=' + attrs['consul_dc'])

    return name, attrs, groups


@parses('triton_machine')
@calculate_mantl_vars
def triton_machine(resource, module_name, *args, **kwargs):
    raw_attrs = resource['primary']['attributes']
    name = raw_attrs.get('name')
    groups = []

    attrs = {
        'id': raw_attrs['id'],
        'dataset': raw_attrs['dataset'],
        'disk': raw_attrs['disk'],
        'firewall_enabled': parse_bool(raw_attrs['firewall_enabled']),
        'image': raw_attrs['image'],
        'ips': parse_list(raw_attrs, 'ips'),
        'memory': raw_attrs['memory'],
        'name': raw_attrs['name'],
        'networks': parse_list(raw_attrs, 'networks'),
        'package': raw_attrs['package'],
        'primary_ip': raw_attrs['primaryip'],
        'root_authorized_keys': raw_attrs['root_authorized_keys'],
        'state': raw_attrs['state'],
        'tags': parse_dict(raw_attrs, 'tags'),
        'type': raw_attrs['type'],
        'user_data': raw_attrs['user_data'],
        'user_script': raw_attrs['user_script'],

        # ansible
        'ansible_ssh_host': raw_attrs['primaryip'],
        'ansible_ssh_user': 'root',  # it's "root" on Triton by default

        # generic
        'public_ipv4': raw_attrs['primaryip'],
        'provider': 'triton',
    }

    # private IPv4
    for ip in attrs['ips']:
        if ip.startswith('10') or ip.startswith('192.168'):  # private IPs
            attrs['private_ipv4'] = ip
            break

    if 'private_ipv4' not in attrs:
        attrs['private_ipv4'] = attrs['public_ipv4']

    # attrs specific to Mantl
    attrs.update({
        'consul_dc': _clean_dc(attrs['tags'].get('dc', 'none')),
        'role': attrs['tags'].get('role', 'none'),
        'ansible_python_interpreter': attrs['tags'].get('python_bin', 'python')
    })

    # add groups based on attrs
    groups.append('triton_image=' + attrs['image'])
    groups.append('triton_package=' + attrs['package'])
    groups.append('triton_state=' + attrs['state'])
    groups.append('triton_firewall_enabled=%s' % attrs['firewall_enabled'])
    groups.extend('triton_tags_%s=%s' % item
                  for item in list(attrs['tags'].items()))
    groups.extend('triton_network=' + network
                  for network in attrs['networks'])

    # groups specific to Mantl
    groups.append('role=' + attrs['role'])
    groups.append('dc=' + attrs['consul_dc'])

    return name, attrs, groups


@parses('packet_device')
@calculate_mantl_vars
def packet_device(resource, tfvars=None):
    raw_attrs = resource['primary']['attributes']
    name = raw_attrs['id']
    groups = []

    attrs = {
        'id': raw_attrs['id'],
        'facility': raw_attrs['facility'],
        'hostname': raw_attrs['hostname'],
        'operating_system': raw_attrs['operating_system'],
        'locked': parse_bool(raw_attrs['locked']),
        'metadata': json.loads(raw_attrs.get('user_data', '{}')),
        'plan': raw_attrs['plan'],
        'project_id': raw_attrs['project_id'],
        'state': raw_attrs['state'],
        # ansible
        'ansible_ssh_host': raw_attrs['network.0.address'],
        'ansible_ssh_user': 'root',  # it's always "root" on Packet
        # generic
        'ipv4_address': raw_attrs['network.0.address'],
        'public_ipv4': raw_attrs['network.0.address'],
        'ipv6_address': raw_attrs['network.1.address'],
        'public_ipv6': raw_attrs['network.1.address'],
        'private_ipv4': raw_attrs['network.2.address'],
        'provider': 'packet',
    }

    # attrs specific to Mantl
    attrs.update({
        'consul_dc': _clean_dc(attrs['metadata'].get('dc', attrs['facility'])),
        'role': attrs['metadata'].get('role', 'none'),
        'ansible_python_interpreter': attrs['metadata']
        .get('python_bin', 'python')
    })

    # add groups based on attrs
    groups.append('packet_facility=' + attrs['facility'])
    groups.append('packet_operating_system=' + attrs['operating_system'])
    groups.append('packet_locked=%s' % attrs['locked'])
    groups.append('packet_state=' + attrs['state'])
    groups.append('packet_plan=' + attrs['plan'])
    groups.extend('packet_metadata_%s=%s' % item
                  for item in attrs['metadata'].items())

    # groups specific to Mantl
    groups.append('role=' + attrs['role'])
    groups.append('dc=' + attrs['consul_dc'])

    return name, attrs, groups


@parses('digitalocean_droplet')
@calculate_mantl_vars
def digitalocean_host(resource, tfvars=None, **kwargs):
    raw_attrs = resource['primary']['attributes']
    name = raw_attrs['name']
    groups = []

    attrs = {
        'id': raw_attrs['id'],
        'image': raw_attrs['image'],
        'ipv4_address': raw_attrs['ipv4_address'],
        'locked': parse_bool(raw_attrs['locked']),
        'metadata': json.loads(raw_attrs.get('user_data', '{}')),
        'region': raw_attrs['region'],
        'size': raw_attrs['size'],
        'ssh_keys': parse_list(raw_attrs, 'ssh_keys'),
        'status': raw_attrs['status'],
        'tags': parse_list(raw_attrs, 'tags'),
        # ansible
        'ansible_ssh_host': raw_attrs['ipv4_address'],
        'ansible_ssh_user': 'root',  # it's always "root" on DO
        # generic
        'public_ipv4': raw_attrs['ipv4_address'],
        'private_ipv4': raw_attrs.get('ipv4_address_private',
                                      raw_attrs['ipv4_address']),
        'provider': 'digitalocean',
    }

    # attrs specific to Mantl
    attrs.update({
        'consul_dc': _clean_dc(attrs['metadata'].get('dc', attrs['region'])),
        'role': attrs['metadata'].get('role', 'none'),
        'ansible_python_interpreter': attrs['metadata']
        .get('python_bin', 'python')
    })

    # add groups based on attrs
    groups.append('do_image=' + attrs['image'])
    groups.append('do_locked=%s' % attrs['locked'])
    groups.append('do_region=' + attrs['region'])
    groups.append('do_size=' + attrs['size'])
    groups.append('do_status=' + attrs['status'])
    groups.extend('do_metadata_%s=%s' % item
                  for item in attrs['metadata'].items())
    groups.extend('do_tag=%s' % item
                  for item in attrs['tags'])

    # groups specific to Mantl
    groups.append('role=' + attrs['role'])
    groups.append('dc=' + attrs['consul_dc'])

    return name, attrs, groups


@parses('softlayer_virtualserver')
@calculate_mantl_vars
def softlayer_host(resource, module_name, **kwargs):
    raw_attrs = resource['primary']['attributes']
    name = raw_attrs['name']
    groups = []

    attrs = {
        'id': raw_attrs['id'],
        'image': raw_attrs['image'],
        'ipv4_address': raw_attrs['ipv4_address'],
        'metadata': json.loads(raw_attrs.get('user_data', '{}')),
        'region': raw_attrs['region'],
        'ram': raw_attrs['ram'],
        'cpu': raw_attrs['cpu'],
        'ssh_keys': parse_list(raw_attrs, 'ssh_keys'),
        'public_ipv4': raw_attrs['ipv4_address'],
        'private_ipv4': raw_attrs['ipv4_address_private'],
        'ansible_ssh_host': raw_attrs['ipv4_address'],
        'ansible_ssh_user': 'root',
        'provider': 'softlayer',
    }

    # attrs specific to Mantl
    attrs.update({
        'consul_dc': _clean_dc(attrs['metadata'].get('dc', attrs['region'])),
        'role': attrs['metadata'].get('role', 'none'),
        'ansible_python_interpreter': attrs['metadata']
        .get('python_bin', 'python')
    })

    # groups specific to Mantl
    groups.append('role=' + attrs['role'])
    groups.append('dc=' + attrs['consul_dc'])

    return name, attrs, groups


@parses('openstack_compute_instance_v2')
@calculate_mantl_vars
def openstack_host(resource, module_name, **kwargs):
    raw_attrs = resource['primary']['attributes']
    name = raw_attrs['name']
    groups = []

    attrs = {
        'access_ip_v4': raw_attrs['access_ip_v4'],
        'access_ip_v6': raw_attrs['access_ip_v6'],
        'flavor': parse_dict(raw_attrs, 'flavor',
                             sep='_'),
        'id': raw_attrs['id'],
        'image': parse_dict(raw_attrs, 'image',
                            sep='_'),
        'key_pair': raw_attrs['key_pair'],
        'metadata': parse_dict(raw_attrs, 'metadata'),
        'network': parse_attr_list(raw_attrs, 'network'),
        'region': raw_attrs.get('region', ''),
        'security_groups': parse_list(raw_attrs, 'security_groups'),
        # ansible
        # workaround for an OpenStack bug where hosts have a different domain
        # after they're restarted
        'host_domain': 'novalocal',
        'use_host_domain': True,
        # generic
        'public_ipv4': raw_attrs['access_ip_v4'],
        'private_ipv4': raw_attrs['access_ip_v4'],
        'provider': 'openstack',
    }

    if 'floating_ip' in raw_attrs:
        attrs['private_ipv4'] = raw_attrs['network.0.fixed_ip_v4']

    try:
        attrs.update({
            'ansible_ssh_host': raw_attrs['access_ip_v4'],
            'publicly_routable': True,
        })
    except (KeyError, ValueError):
        attrs.update({'ansible_ssh_host': '', 'publicly_routable': False})

    # attrs specific to Ansible
    if 'metadata.ssh_user' in raw_attrs:
        attrs['ansible_ssh_user'] = raw_attrs['metadata.ssh_user']

    # attrs specific to Mantl
    attrs.update({
        'consul_dc': _clean_dc(attrs['metadata'].get('dc', module_name)),
        'role': attrs['metadata'].get('role', 'none'),
        'ansible_python_interpreter': attrs['metadata']
        .get('python_bin', 'python')
    })

    # add groups based on attrs
    if 'name' in attrs['image'].keys():
        groups.append('os_image=' + attrs['image']['name'])
    groups.append('os_flavor=' + attrs['flavor']['name'])
    groups.extend('os_metadata_%s=%s' % item
                  for item in list(attrs['metadata'].items()))
    groups.append('os_region=' + attrs['region'])

    # groups specific to Mantl
    groups.append('role=' + attrs['metadata'].get('role', 'none'))
    groups.append('dc=' + attrs['consul_dc'])

    return name, attrs, groups


@parses('aws_instance')
@calculate_mantl_vars
def aws_host(resource, module_name, **kwargs):
    try:
        name_key = kwargs['args'].aws_name_key
    except KeyError:
        name_key = 'tags.Name'
    try:
        ssh_host_key = kwargs['args'].aws_ssh_host_key
    except KeyError:
        ssh_host_key =  'public_ip'

    try:
      name = resource['primary']['attributes'][name_key]
    except:
      name = resource['primary']['attributes'][ssh_host_key]
    raw_attrs = resource['primary']['attributes']

    groups = []

    attrs = {
        'ami': raw_attrs['ami'],
        'availability_zone': raw_attrs['availability_zone'],
        'ebs_block_device': parse_attr_list(raw_attrs, 'ebs_block_device'),
        'ebs_optimized': parse_bool(raw_attrs['ebs_optimized']),
        'ephemeral_block_device': parse_attr_list(raw_attrs,
                                                  'ephemeral_block_device'),
        'id': raw_attrs['id'],
        'key_name': raw_attrs['key_name'],
        'private': parse_dict(raw_attrs, 'private',
                              sep='_'),
        'public': parse_dict(raw_attrs, 'public',
                             sep='_'),
        'root_block_device': parse_attr_list(raw_attrs, 'root_block_device'),
        'security_groups': parse_list(raw_attrs, 'security_groups'),
        'subnet': parse_dict(raw_attrs, 'subnet',
                             sep='_'),
        'tags': parse_dict(raw_attrs, 'tags'),
        'tenancy': raw_attrs['tenancy'],
        'vpc_security_group_ids': parse_list(raw_attrs,
                                             'vpc_security_group_ids'),
        # ansible-specific
        'ansible_ssh_host': raw_attrs[ssh_host_key],
        # generic
        'public_ipv4': raw_attrs['public_ip'],
        'private_ipv4': raw_attrs['private_ip'],
        'provider': 'aws',
    }

    # attrs specific to Ansible
    if 'tags.sshUser' in raw_attrs:
        attrs['ansible_ssh_user'] = raw_attrs['tags.sshUser']
    if 'tags.sshPrivateIp' in raw_attrs:
        attrs['ansible_ssh_host'] = raw_attrs['private_ip']
    if 'tags.sshPrivateKey' in raw_attrs:
        attrs['ansible_ssh_private_key_file'] = raw_attrs['tags.sshPrivateKey']

    # add to groups by comma separated tag(s)
    if 'tags.groups' in raw_attrs:
        for group in raw_attrs['tags.groups'].split(','):
            groups.append(group)


    # attrs specific to Mantl
    attrs.update({
        'consul_dc': _clean_dc(attrs['tags'].get('dc', module_name)),
        'role': attrs['tags'].get('role', 'none'),
        'ansible_python_interpreter': attrs['tags']
        .get('python_bin', 'python')
    })

    # groups specific to Mantl
    groups.extend(['aws_ami=' + attrs['ami'],
                   'aws_az=' + attrs['availability_zone'],
                   'aws_key_name=' + attrs['key_name'],
                   'aws_tenancy=' + attrs['tenancy']])
    groups.extend('aws_tag_%s=%s' % item for item in list(attrs['tags'].items()))
    groups.extend('aws_vpc_security_group=' + group
                  for group in attrs['vpc_security_group_ids'])
    groups.extend('aws_subnet_%s=%s' % subnet
                  for subnet in list(attrs['subnet'].items()))

    # groups specific to Mantl
    groups.append('role=' + attrs['role'])
    groups.append('dc=' + attrs['consul_dc'])

    return name, attrs, groups


@parses('google_compute_instance')
@calculate_mantl_vars
def gce_host(resource, module_name, **kwargs):
    name = resource['primary']['id']
    raw_attrs = resource['primary']['attributes']
    groups = []

    # network interfaces
    interfaces = parse_attr_list(raw_attrs, 'network_interface')
    for interface in interfaces:
        interface['access_config'] = parse_attr_list(interface,
                                                     'access_config')
        for key in list(interface.keys()):
            if '.' in key:
                del interface[key]

    # general attrs
    attrs = {
        'can_ip_forward': raw_attrs['can_ip_forward'] == 'true',
        'disks': parse_attr_list(raw_attrs, 'disk'),
        'machine_type': raw_attrs['machine_type'],
        'metadata': parse_dict(raw_attrs, 'metadata'),
        'network': parse_attr_list(raw_attrs, 'network'),
        'network_interface': interfaces,
        'self_link': raw_attrs['self_link'],
        'service_account': parse_attr_list(raw_attrs, 'service_account'),
        'tags': parse_list(raw_attrs, 'tags'),
        'zone': raw_attrs['zone'],
        # ansible
        'provider': 'gce',
    }

    # attrs specific to Ansible
    if 'metadata.ssh_user' in raw_attrs:
        attrs['ansible_ssh_user'] = raw_attrs['metadata.ssh_user']

    # attrs specific to Mantl
    attrs.update({
        'consul_dc': _clean_dc(attrs['metadata'].get('dc', module_name)),
        'role': attrs['metadata'].get('role', 'none'),
        'ansible_python_interpreter': attrs['metadata']
        .get('python_bin', 'python')
    })

    try:
        attrs.update({
            'ansible_ssh_host': interfaces[0]['access_config'][0]['nat_ip'] or
            interfaces[0]['access_config'][0]['assigned_nat_ip'],
            'public_ipv4': interfaces[0]['access_config'][0]['nat_ip'] or
            interfaces[0]['access_config'][0]['assigned_nat_ip'],
            'private_ipv4': interfaces[0]['address'],
            'publicly_routable': True,
        })
    except (KeyError, ValueError):
        attrs.update({'ansible_ssh_host': '', 'publicly_routable': False})

    # add groups based on attrs
    groups.extend('gce_image=' + disk['image'] for disk in attrs['disks'])
    groups.append('gce_machine_type=' + attrs['machine_type'])
    groups.extend('gce_metadata_%s=%s' % (key, value)
                  for (key, value) in list(attrs['metadata'].items())
                  if key not in set(['sshKeys']))
    groups.extend('gce_tag=' + tag for tag in attrs['tags'])
    groups.append('gce_zone=' + attrs['zone'])

    if attrs['can_ip_forward']:
        groups.append('gce_ip_forward')
    if attrs['publicly_routable']:
        groups.append('gce_publicly_routable')

    # groups specific to Mantl
    groups.append('role=' + attrs['metadata'].get('role', 'none'))
    groups.append('dc=' + attrs['consul_dc'])

    return name, attrs, groups


@parses('vsphere_virtual_machine')
@calculate_mantl_vars
def vsphere_host(resource, module_name, **kwargs):
    raw_attrs = resource['primary']['attributes']
    network_attrs = parse_dict(raw_attrs, 'network_interface')
    network = parse_dict(network_attrs, '0')
    ip_address = network.get('ipv4_address', network['ip_address'])
    name = raw_attrs['name']
    groups = []

    attrs = {
        'id': raw_attrs['id'],
        'ip_address': ip_address,
        'private_ipv4': ip_address,
        'public_ipv4': ip_address,
        'metadata': parse_dict(raw_attrs, 'custom_configuration_parameters'),
        'provider': 'vsphere',
    }

    try:
        attrs.update({
            'ansible_ssh_host': ip_address,
        })
    except (KeyError, ValueError):
        attrs.update({'ansible_ssh_host': '', })

    attrs.update({
        'consul_dc': _clean_dc(attrs['metadata']
                               .get('consul_dc', module_name)),
        'role': attrs['metadata'].get('role', 'none'),
        'ansible_python_interpreter': attrs['metadata']
        .get('python_bin', 'python')
    })

    # attrs specific to Ansible
    if 'ssh_user' in attrs['metadata']:
        attrs['ansible_ssh_user'] = attrs['metadata']['ssh_user']

    groups.append('role=' + attrs['role'])
    groups.append('dc=' + attrs['consul_dc'])

    return name, attrs, groups


@parses('azurerm_virtual_machine')
@calculate_mantl_vars
def azurerm_host(resource, module_name, **kwargs):
    name = resource['primary']['attributes']['name']
    raw_attrs = resource['primary']['attributes']

    groups = []

    # Is windows os ?
    is_windows = False
    for attr in resource['primary']['attributes']:
        if attr.endswith(".publisher") and resource['primary']['attributes'].get(attr).find("Windows") != -1:
            is_windows = True

    attrs = {
        'id': raw_attrs['id'],
        'name': raw_attrs['name'],
        # ansible
        'ansible_ssh_user': raw_attrs.get('tags.ssh_user', ''),
        'ansible_ssh_host': raw_attrs.get('tags.ssh_ip', ''),
    }
    if is_windows:
        attrs['ansible_user'] = raw_attrs.get('tags.ssh_user', '')
        attrs['ansible_port'] = 5986
        attrs['ansible_connection'] = 'winrm'
        attrs['ansible_winrm_server_cert_validation'] = 'ignore'

    groups.append('role=' + raw_attrs.get('tags.role', ''))

    return name, attrs, groups


@parses('azure_instance')
@calculate_mantl_vars
def azure_host(resource, module_name, **kwargs):
    name = resource['primary']['attributes']['name']
    raw_attrs = resource['primary']['attributes']

    groups = []

    attrs = {
        'automatic_updates': raw_attrs['automatic_updates'],
        'description': raw_attrs['description'],
        'hosted_service_name': raw_attrs['hosted_service_name'],
        'id': raw_attrs['id'],
        'image': raw_attrs['image'],
        'ip_address': raw_attrs['ip_address'],
        'location': raw_attrs['location'],
        'name': raw_attrs['name'],
        'reverse_dns': raw_attrs['reverse_dns'],
        'security_group': raw_attrs['security_group'],
        'size': raw_attrs['size'],
        'ssh_key_thumbprint': raw_attrs['ssh_key_thumbprint'],
        'subnet': raw_attrs['subnet'],
        'username': raw_attrs['username'],
        'vip_address': raw_attrs['vip_address'],
        'virtual_network': raw_attrs['virtual_network'],
        'endpoint': parse_attr_list(raw_attrs, 'endpoint'),
        # ansible
        'ansible_ssh_user': raw_attrs['username'],
        'ansible_ssh_host': raw_attrs['vip_address'],
    }

    for ep in attrs['endpoint']:
        if ep['name'] == 'SSH':
            attrs['ansible_ssh_port'] = int(ep['public_port'])

    # attrs specific to mantl
    attrs.update({
        'consul_dc': attrs['location'].lower().replace(" ", "-"),
        'role': attrs['description']
    })

    # groups specific to mantl
    groups.extend(['azure_image=' + attrs['image'],
                   'azure_location=' + attrs['location']
                   .lower().replace(" ", "-"),
                   'azure_username=' + attrs['username'],
                   'azure_security_group=' + attrs['security_group']])

    # groups specific to mantl
    groups.append('role=' + attrs['role'])
    groups.append('dc=' + attrs['consul_dc'])

    return name, attrs, groups


@parses('clc_server')
@calculate_mantl_vars
def clc_server(resource, module_name, **kwargs):
    raw_attrs = resource['primary']['attributes']
    name = raw_attrs.get('id')
    groups = []
    md = parse_dict(raw_attrs, 'metadata')
    attrs = {
        'metadata': md,
        'ansible_ssh_user': md.get('ssh_user', 'root'),
        'provider': 'clc',
        'publicly_routable': False,
    }

    if 'ssh_port' in md:
        attrs['ansible_ssh_port'] = md.get('ssh_port')

    try:
        attrs.update({
            'public_ipv4': raw_attrs['public_ip_address'],
            'private_ipv4': raw_attrs['private_ip_address'],
            'ansible_ssh_host': raw_attrs['public_ip_address'],
            'publicly_routable': True,
        })
    except (KeyError, ValueError):
        attrs.update({
            'ansible_ssh_host': raw_attrs['private_ip_address'],
            'private_ipv4': raw_attrs['private_ip_address'],
        })

    attrs.update({
        'consul_dc': _clean_dc(attrs['metadata'].get('dc', module_name)),
        'role': attrs['metadata'].get('role', 'none'),
    })

    groups.append('role=' + attrs['role'])
    groups.append('dc=' + attrs['consul_dc'])
    return name, attrs, groups


@parses('ucs_service_profile')
@calculate_mantl_vars
def ucs_host(resource, module_name, **kwargs):
    name = resource['primary']['id']
    raw_attrs = resource['primary']['attributes']
    groups = []

    # general attrs
    attrs = {
        'metadata': parse_dict(raw_attrs, 'metadata'),
        'provider': 'ucs',
    }

    # attrs specific to mantl
    attrs.update({
        'consul_dc': _clean_dc(attrs['metadata'].get('dc', module_name)),
        'role': attrs['metadata'].get('role', 'none'),
    })

    try:
        attrs.update({
            'ansible_ssh_host': raw_attrs['vNIC.0.ip'],
            'public_ipv4': raw_attrs['vNIC.0.ip'],
            'private_ipv4': raw_attrs['vNIC.0.ip']
        })
    except (KeyError, ValueError):
        attrs.update({'ansible_ssh_host': '', 'publicly_routable': False})

    # add groups based on attrs
    groups.append('role=' + attrs['role'])  # .get('role', 'none'))

    # groups.append('all:children')
    groups.append('dc=' + attrs['consul_dc'])

    return name, attrs, groups

@parses('scaleway_server')
@calculate_mantl_vars
def scaleway_host(resource, tfvars=None):
    raw_attrs = resource['primary']['attributes']
    name = raw_attrs['name']
    groups = []

    attrs = {
        'enable_ipv6': raw_attrs['enable_ipv6'],
        'id': raw_attrs['id'],
        'image': raw_attrs['image'],
        'name': raw_attrs['name'],
        'private_ip': raw_attrs['private_ip'],
        'public_ip': raw_attrs['public_ip'],
        'state': raw_attrs['state'],
        'state_detail': raw_attrs['state_detail'],
        'tags': parse_list(raw_attrs, 'tags'),
        'type': raw_attrs['type'],
        # ansible
        'ansible_ssh_host': raw_attrs['public_ip'],
        'ansible_ssh_user': 'root',  # it's always "root" on DO
        # generic
        'public_ipv4': raw_attrs['public_ip'],
        'private_ipv4': raw_attrs['private_ip'],
        'provider': 'scaleway',
    }


    # attrs specific to Ansible
    if 'tags.sshUser' in raw_attrs:
        attrs['ansible_ssh_user'] = raw_attrs['tags.sshUser']
    if 'tags.sshPrivateIp' in raw_attrs:
        attrs['ansible_ssh_host'] = raw_attrs['private_ip']

    # add groups based on attrs
    groups.append('scaleway_image=' + attrs['image'])
    groups.append('scaleway_type=' + attrs['type'])
    groups.append('scaleway_state=' + attrs['state'])
    groups.extend('scaleway_tag=%s' % item
                  for item in attrs['tags'])

    return name, attrs, groups


# QUERY TYPES
def query_host(hosts, target):
    for name, attrs, _ in hosts:
        if name == target:
            return attrs

    return {}


def query_list(hosts):
    groups = defaultdict(dict)
    meta = {}

    for name, attrs, hostgroups in hosts:
        for group in set(hostgroups):
            groups[group].setdefault('hosts', [])
            groups[group]['hosts'].append(name)

        meta[name] = attrs

    groups['_meta'] = {'hostvars': meta}
    return groups


def query_hostfile(hosts):
    out = ['## begin hosts generated by terraform.py ##']
    out.extend(
        '{}\t{}'.format(attrs['ansible_ssh_host'].ljust(16), name)
        for name, attrs, _ in hosts
    )

    out.append('## end hosts generated by terraform.py ##')
    return '\n'.join(out)
