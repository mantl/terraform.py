# Terraform.py

[![Build Status](https://travis-ci.org/CiscoCloud/terraform.py.svg)](https://travis-ci.org/CiscoCloud/terraform.py)

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc/generate-toc again -->
**Table of Contents**

- [Terraform.py](#terraformpy)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Releases](#releases)
    - [Adding a new provider](#adding-a-new-provider)
        - [Common Utilities](#common-utilities)
            - [`parse_attr_list`](#parseattrlist)
            - [`parse_dict`](#parsedict)
            - [`parse_list`](#parselist)
    - [License](#license)

<!-- markdown-toc end -->

`terraform.py` is a dynamic Ansible inventory script to connect to systems by
reading Terraform's `.tfstate` files. It currently supports:

 - AWS ([`aws_instance`](https://www.terraform.io/docs/providers/aws/r/instance.html))
 - Google Cloud ([`google_compute_instance`](https://www.terraform.io/docs/providers/google/r/compute_instance.html))
 - Openstack ([`openstack_compute_instance_v2`'](https://www.terraform.io/docs/providers/openstack/r/compute_instance_v2.html))
 - DigitalOcean ([`digitalocean_droplet`](http://terraform.io/docs/providers/do/r/droplet.html))
 - Azure ([`azure_instance`](https://www.terraform.io/docs/providers/azure/r/instance.html))
 - VMware vSphere ([`vsphere_virtual_machine`](https://www.terraform.io/docs/providers/vsphere/r/virtual_machine.html))
 - CenturyLinkCloud ([`clc_server`](https://www.terraform.io/docs/providers/clc/r/server.html))
 - SoftLayer ([`softlayer_virtualserver`](https://github.com/finn-no/terraform-provider-softlayer)) (Unofficial)

## Installation

`terraform.py` just needs to be on the filesystem of your control machine and
marked as executable. If you're distributing your Ansible configuration via git,
you could just add this repository as a git submodule and pin it to the
[release](#releases) you want. Otherwise, copying `terraform.py` to a convenient
place on your filesystem should do the trick.

## Usage

Make sure that you've annotated your resources with "tags" that correspond to the sshUser for the machine.

Example, for EC2 resources, add a [tags](https://www.terraform.io/docs/providers/aws/r/instance.html#tags) entry of "sshUser" equal to "ec2-user":
	
	tags {
      Name = "cheese"
      sshUser = "ec2-user"
    }

Next, specify `terraform.py` as an inventory source for any Ansible command. For
instance, to use this to test if your servers are working:

    ansible -i terraform.py -m ping all

Or in a playbook:

    ansible-playbook -i terraform.py your_playbook.yml

## Releases

`terraform.py` is with matching versions of
[mantl](https://github.com/CiscoCloud/mantl). Run `terraform.py --version` to
report the current version.

## Adding a new provider

To add a new provider, you need to implement a parser for that provider's
resources in `terraform.py`. Parsers should only be implemented for resources
that Ansible can connect to and modify (instances, nodes, whatever your platform
calls them.) A parser is a function that takes a resource (a dictionary
processed from JSON) and outputs a tuple of `(name, attributes, groups)`. The
parser should be decorated with the `parses` decorator, which takes the name of
the resource (EG `aws_instance`). It should also be decorated with
`calculate_mantl_vars`.

As a guideline, `terraform.py` should require no resources outside the Python
standard distribution so it can just be copied in wherever it's needed.

### Common Utilities

Terraform's state files represent node attributes as a flat dictionary, but
contain nested information within them. This tends to look something like this:

    ...
    "disk.#": 1,
    "disk.0.auto_delete": "true",
    "disk.0.device_name": ""
    ...

It's much easier to work with nested information in Ansible, so `terraform.py`
has three sub-parsers to transform these structures:

#### `parse_attr_list`

`parse_attr_list` takes a dictionary, a prefix, and an optional separator and
returns a list of dictionaries. The limited "disk" example above would become:

    [{"auto_delete": "true", "device_name": ""}]

#### `parse_dict`

`parse_dict` takes a dictionary, a prefix, and an optional separator and returns
a dictionary. Given keys like this and the prefix "metadata":

    ...
    "metadata.#": "3",
    "metadata.dc": "gce-dc"
    ...

`parse_dict` would return something like this:

    {"dc": "gce-dc"}

#### `parse_list`

Lists are rarer in Terraform states, but still occur in things like tag lists.
`parse_list` takes a dictionary, a prefix, and an optional separator and returns
a list. Given keys like this and the prefix "keys":

    ...
    "tags.#": "2",
    "tags.2783239913": "mantl",
    "tags.3990563915": "control",
    ...

`parse_list` would return this:

    ["mantl", "control"]

## License

Copyright © 2015 Cisco Systems, Inc.

Licensed under the
[Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0) (the
"License").

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
