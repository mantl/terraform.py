# -*- coding: utf-8 -*-
import argparse
import json
import os

from ati import __name__, __version__ 
from ati.terraform import get_stage_root, iterhosts, iterresources, query_host, query_hostfile, query_list, tfstates

def cli():
    parser = argparse.ArgumentParser(
        __file__, __doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--list',
                       action='store_true',
                       help='list all variables')
    modes.add_argument('--host', help='list variables for a single host')
    modes.add_argument('--version',
                       action='store_true',
                       help='print version and exit')
    modes.add_argument('--hostfile',
                       action='store_true',
                       help='print hosts as a /etc/hosts snippet')
    parser.add_argument('--pretty',
                        action='store_true',
                        help='pretty-print output JSON')
    parser.add_argument('--nometa',
                        action='store_true',
                        help='with --list, exclude hostvars')
    default_root = os.environ.get('TERRAFORM_STATE_ROOT', os.getcwd())
    parser.add_argument('--root',
                        default=default_root,
                        help='custom root to search for `.tfstate`s in')

    args = parser.parse_args()

    staged_root = get_stage_root(root=args.root)
    if staged_root != args.root:
        args.root = staged_root

    if args.version:
        print('{} {}s'.format(__name__, __version__))
        parser.exit()

    hosts = iterhosts(iterresources(tfstates(args.root)))
    if args.list:
        output = query_list(hosts)
        if args.nometa:
            del output['_meta']
        print(json.dumps(output, indent=4 if args.pretty else None))
    elif args.host:
        output = query_host(hosts, args.host)
        print(json.dumps(output, indent=4 if args.pretty else None))
    elif args.hostfile:
        output = query_hostfile(hosts)
        print(output)

    parser.exit()
