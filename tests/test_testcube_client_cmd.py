#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_testcube_client
----------------------------------

Tests for `testcube_client` module. Requires a testcube server.
"""

import unittest

from click.testing import CliRunner

from testcube_client import cli

server = 'http://127.0.0.1:8000'


class TestCases(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_command_line_interface(self):
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'testcube_client.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
