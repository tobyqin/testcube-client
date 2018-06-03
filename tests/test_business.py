#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for `business` module. Requires a testcube server.
"""

import unittest
from os import chdir

from testcube_client import business
from testcube_client import request_client as client
from testcube_client.request_helper import *
from testcube_client.result_parser import get_results, get_files
from testcube_client.settings import enable_debug_log
from tests.default.test_xunit_parser import xunit_xml, xunit_dir

server = 'http://127.0.0.1:8000'


class TestCases(unittest.TestCase):
    def setUp(self):
        enable_debug_log()
        register_client(server, force=True)
        self.team = business.get_or_create_team('Core')
        self.product = business.get_or_create_product('TestCube', self.team)
        chdir(xunit_dir)

    def tearDown(self):
        pass

    def test_get_or_create_team(self):
        team = business.get_or_create_team('Dog')
        logging.info(team)
        assert 'teams/' in team

        team1 = business.get_or_create_team('Dog')
        assert team == team1

    def test_get_or_create_product(self):
        product = business.get_or_create_product('testcube', self.team)
        logging.info(product)
        assert 'products/' in product

        product1 = business.get_or_create_product('testcube', self.team, 'v1.0')
        assert 'products/' in product1
        assert product != product1

        product2 = business.get_or_create_product('testcube', self.team, 'v1.0')
        assert product2 == product1

    def test_get_or_create_testcase(self):
        obj = business.get_or_create_testcase(name='testcube test',
                                              full_name='test.testcube',
                                              product_url=self.product)
        logging.info(obj)
        assert 'cases/' in obj

        val1 = business.get_or_create_testcase(name='testcube test1',
                                               full_name='test.testcube',
                                               product_url=self.product)
        assert 'cases/' in val1
        assert obj != val1

        val2 = business.get_or_create_testcase(name='testcube test1',
                                               full_name='test.testcube',
                                               product_url=self.product)
        assert val2 == val1

    def test_get_or_create_client(self):
        c = business.get_or_create_client()
        logging.info(c)
        assert 'clients/' in c

        detail = client.get_obj(c)
        logging.info(detail)
        assert detail['name'] is not None

    def test_start_run(self):
        run_url = business.start_run(team_name='Core',
                                     product_name='TestCube')

        logging.info(run_url)
        assert 'current_run' in config
        assert config['current_run']['url'] == run_url
        return run_url

    def test_finish_run(self):
        run_url = business.start_run(team_name='Core',
                                     product_name='TestCube',
                                     run_name='my unit test run')

        logging.info(run_url)
        assert 'current_run' in config
        assert config['current_run']['url'] == run_url

        business.finish_run('re*.xml')

    def test_create_result(self):
        results, info = get_results([xunit_xml])
        self.test_start_run()
        run = config['current_run']

        for result in results:
            r = business.create_result(run, result)
            logging.info(r)

    def test_upload_file_pattern(self):
        run_url = business.start_run(team_name='Core',
                                     product_name='TestCube',
                                     run_name='my unit test run')

        for file in get_files('*.png'):
            business.upload_result_file(file, run_url)

        for file in get_files('*.xml'):
            business.upload_result_file(file, run_url)

    def test_upload_file_batch(self):
        business.start_run(team_name='Core',
                           product_name='TestCube',
                           run_name='my unit test run')

        business.upload_files('*.png')

    def test_handle_task(self):
        business.handle_task()

    def test_reset_result(self):
        business.start_run(team_name='Core',
                           product_name='TestCube',
                           run_name='my unit test run')

        business.finish_run('re*.xml')
        business.reset_result(1, '*.xml')


if __name__ == '__main__':
    unittest.main()
