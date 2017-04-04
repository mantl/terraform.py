# -*- coding: utf-8 -*-
import json

import ati.remote

def test_is_remote_state():
    tf = None
    with open('tests/fixtures/remote_init.json', 'r') as f:
        tf = json.load(f)

    assert callable(ati.remote.get_remote_func(tf))

def test_not_remote_state():
    tf = None
    with open('tests/fixtures/local_init.json', 'r') as f:
        tf = json.load(f)

    assert ati.remote.get_remote_func(tf) is None
