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
from testcube_client import testcube_client as client
from testcube_client.request_helper import *

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

    def test_api_post(self):
        api = 'teams'
        data = {'name': 'EggPlant', 'owner': 'toby.qin'}
        result = client.post(api, data)
        print(result)
        assert result['name'] == data['name']
        assert result['owner'] == data['owner']

    def test_api_get(self):
        self.test_api_post()

        api = 'teams'
        result = client.get(api, params={'name': 'EggPlant'})
        print(result)
        assert result['count'] >= 1
        assert isinstance(result['results'], list)
        return result

    def test_api_get_object(self):
        result = self.test_api_get()
        first = result['results'][0]
        get_first = client.get_obj(first['url'])
        assert first == get_first

    def test_api_put(self):
        api = 'teams'
        teams = self.test_api_get()['results']

        for team in teams:
            team_url = team['url']
            print('update team: {}'.format(team_url))
            client.put(team_url, data={'name': 'Dog'})

        new_teams = client.get(api, params={'name': 'Dog'})['results']
        for team in new_teams:
            print(team)
            assert team['name'] == 'Dog'

    def test_api_delete(self):
        api = 'teams'
        egg_teams = self.test_api_get()['results']
        for team in egg_teams:
            client.delete(team['url'])

        teams = client.get(api, params={'name': 'EggPlant'})
        assert teams['count'] == 0

        dog_teams = client.get(api, params={'name': 'Dog'})['results']
        deleted_team = egg_teams[0]

        for team in dog_teams:
            client.delete(team['url'])

        teams = client.get(api, params={'name': 'Dog'})
        assert teams['count'] == 0

        try:
            client.delete(deleted_team['url'])
        except ValueError as e:
            print('cannot deleted twice! ' + str(e))

    def test_command_line_interface(self):
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'testcube_client.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
