import unittest
import os
from os.path import dirname, join
import xunitparser

test_dir = dirname(__file__)
xunit_dir = join(test_dir, 'xunits')
xunit_xml = join(xunit_dir, 'results.xml')


class TestCases(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_basic_parser(self):
        suite, result = xunitparser.parse(open(xunit_xml))
        assert isinstance(suite, unittest.TestSuite)
        assert isinstance(result, unittest.TestResult)

        print suite
        print result
