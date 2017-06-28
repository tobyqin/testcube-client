#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for `business` module. Requires a testcube server.
"""

import unittest
from os import chdir

from faker import Faker

from testcube_client import business
from testcube_client.request_helper import *

fake = Faker()

server = 'http://127.0.0.1:8000'
result_dir = r'C:\temp'


class TestCases(unittest.TestCase):
    def setUp(self):
        register_client(server, force=True)
        self.team = business.get_or_create_team('Core')
        self.product = business.get_or_create_product('TestCube')
        chdir(result_dir)

    def tearDown(self):
        pass

    def test_add_run_steps(self):
        run_url = business.start_run(team_name='Core',
                                     product_name='TestCube',
                                     run_name=fake.text(100))

        print(run_url)

        business.finish_run('re*.xml')

    def test_add_run_one(self):
        run_url = business.run(team_name='Core',
                               product_name='TestCube',
                               run_name=fake.text(100),
                               result_xml_pattern='re*.xml')

        print(run_url)


if __name__ == '__main__':
    unittest.main()
