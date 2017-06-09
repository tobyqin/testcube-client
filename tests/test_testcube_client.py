#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_testcube_client
----------------------------------

Tests for `testcube_client` module.
"""

import sys
import unittest
from contextlib import contextmanager
from click.testing import CliRunner
from testcube_client.request_helper import *

from testcube_client import testcube_client as client
from testcube_client import cli
from random import randint

server = 'http://127.0.0.1:8000'


class TestCases(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_register_client(self):
        register_info = register_client(server)
        print(register_info)
        assert register_info['client'] is not None
        assert register_info['token'] is not None

    def test_basic_api_post(self):
        api = 'projects'
        data = {'name': 'EggPlant', 'owner': 'toby.qin'}
        result = client.post(api, data)
        print(result)

        data = {'key': 'test', 'value': 'hello', 'id': result['id']}
        result = client.put(api, data)
        print(result)

    def test_command_line_interface(self):
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'testcube_client.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
