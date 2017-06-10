#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_testcube_client
----------------------------------

Tests for `testcube_client` module. Requires a testcube server.
"""

import unittest

from testcube_client import business
from testcube_client import testcube_client as client
from testcube_client.request_helper import *

server = 'http://127.0.0.1:8000'


class TestCases(unittest.TestCase):
    def setUp(self):
        register_client(server)

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
                                              team='Core',
                                              product='testcube')
        print(obj)
        assert 'cases/' in obj

        val1 = business.get_or_create_testcase(name='testcube test1',
                                               full_name='test.testcube',
                                               team='Core',
                                               product='testcube')
        assert 'cases/' in val1
        assert obj != val1

        val2 = business.get_or_create_testcase(name='testcube test1',
                                               full_name='test.testcube',
                                               team='Core',
                                               product='testcube')
        assert val2 == val1

    def test_get_or_create_client(self):
        client = business.get_or_create_client()
        print(client)

    def test_update_or_create_result(self):
        from tests.default.test_xunit_parser import xunit_xml
        from testcube_client.result_parser import get_results
        results, info = get_results([xunit_xml])
        run = client.get(API.run)['results'][0]

        r1 = business.update_or_create_result(run, results[0])
        r2 = business.update_or_create_result(run, results[0])

        assert r1 == r2
