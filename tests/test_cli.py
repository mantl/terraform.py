# -*- coding: utf-8 -*-
import argparse
import sys

import pytest

from ati import cli, __version__

class FakeNS:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.mark.parametrize("opt1", ['--list', '--host', '--version', '--hostfile'])
@pytest.mark.parametrize("opt2", ['--list', '--host', '--version', '--hostfile'])
def test_list_exclusivity(opt1, opt2, monkeypatch):
    args = ['/bin/ati']

    # this will also test that we complain if none of these are passed
    if opt1 != opt2:
        args += [opt1, opt2]
    monkeypatch.setattr(sys, 'argv', args)

    with pytest.raises(SystemExit):
        _, _ = cli.get_args()


def test_get_args_return_type(monkeypatch):
    args = ['bin/ati', '--list']
    monkeypatch.setattr(sys, 'argv', args)

    args, parser = cli.get_args()

    assert type(args) == argparse.Namespace
    assert type(parser) == argparse.ArgumentParser


def test_terraform_state_root_env_var_sets_root(monkeypatch):
    args = ['bin/ati', '--list']
    monkeypatch.setattr(sys, 'argv', args)
    monkeypatch.setenv('TERRAFORM_STATE_ROOT', '/terraform')

    args, _ = cli.get_args()

    assert args.root == '/terraform'

def test_aws_defaults(monkeypatch):
    args = ['bin/ati', '--list']
    monkeypatch.setattr(sys, 'argv', args)
    args, _ = cli.get_args()

    assert args.aws_ssh_host_key == 'public_ip'
    assert args.aws_name_key == 'tags.Name'


def test_version_output(monkeypatch, capsys):
    args = ['bin/ati', '--list']
    monkeypatch.setattr(sys, 'argv', args)

    def ns():
        return FakeNS(version = '1.0'), argparse.ArgumentParser()
    monkeypatch.setattr(cli, 'get_args', ns)
    with pytest.raises(SystemExit):
        cli.cli()
    out, err = capsys.readouterr()

    # This test is currently mostly a placeholder to demonstrate cli testing
    assert __version__ in out
    assert 'ati' in out
