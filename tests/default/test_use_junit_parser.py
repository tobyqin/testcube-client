import unittest
from os.path import dirname, join
from codecs import open
from testcube_client.xunitparser import parse

test_dir = dirname(dirname(__file__))
xunit_dir = join(test_dir, 'xunits')
xunit_xml = join(xunit_dir, 'results.xml')


class TestCases(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_basic_parser(self):
        suite, result = parse(open(xunit_xml, encoding='utf-8'))
        assert isinstance(suite, unittest.TestSuite)
        assert isinstance(result, unittest.TestResult)

        print(suite)
        print(result)
