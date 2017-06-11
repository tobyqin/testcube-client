#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_testcube_client
----------------------------------

Tests for `testcube_client` module. Requires a testcube server.
"""

import unittest
from os import chdir

from testcube_client import business
from testcube_client import testcube_client as client
from testcube_client.request_helper import *
from testcube_client.result_parser import get_results
from tests.default.test_xunit_parser import xunit_xml, xunit_dir

server = 'http://127.0.0.1:8000'


class TestCases(unittest.TestCase):
    def setUp(self):
        register_client(server)
        self.team = business.get_or_create_team('Core')
        self.product = business.get_or_create_product('TestCube')
        chdir(xunit_dir)

    def tearDown(self):
        pass

    def test_get_or_create_team(self):
        team = business.get_or_create_team('Dog')
        print(team)
        assert 'teams/' in team

        team1 = business.get_or_create_team('Dog')
        assert team == team1

    def test_get_or_create_product(self):
        product = business.get_or_create_product('testcube')
        print(product)
        assert 'products/' in product

        product1 = business.get_or_create_product('testcube', 'v1.0')
        assert 'products/' in product1
        assert product != product1

        product2 = business.get_or_create_product('testcube', 'v1.0')
        assert product2 == product1

    def test_get_or_create_testcase(self):
        obj = business.get_or_create_testcase(name='testcube test',
                                              full_name='test.testcube',
                                              team_url=self.team,
                                              product_url=self.product)
        print(obj)
        assert 'cases/' in obj

        val1 = business.get_or_create_testcase(name='testcube test1',
                                               full_name='test.testcube',
                                               team_url=self.team,
                                               product_url=self.product)
        assert 'cases/' in val1
        assert obj != val1

        val2 = business.get_or_create_testcase(name='testcube test1',
                                               full_name='test.testcube',
                                               team_url=self.team,
                                               product_url=self.product)
        assert val2 == val1

    def test_get_or_create_client(self):
        c = business.get_or_create_client()
        print(c)
        assert 'clients/' in c

        detail = client.get_obj(c)
        print(detail)
        assert detail['name'] is not None

    def test_start_run(self):
        run_url = business.start_run(team_name='Core',
                                     product_name='TestCube')

        print(run_url)
        assert 'current_run' in config
        assert config['current_run']['url'] == run_url
        return run_url

    def test_finish_run(self):
        run_url = business.start_run(team_name='Core',
                                     product_name='TestCube',
                                     run_name='my unit test run')

        print(run_url)
        assert 'current_run' in config
        assert config['current_run']['url'] == run_url

        business.finish_run('re*.xml')

    def test_create_result(self):
        results, info = get_results([xunit_xml])
        self.test_start_run()
        run = config['current_run']

        for result in results:
            r = business.create_result(run, result)
            print(r)
