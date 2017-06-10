import unittest
from codecs import open
from os import chdir
from os.path import dirname, join, curdir, realpath

from testcube_client.result_parser import get_files, get_results
from testcube_client.utils.xunitparser import parse

test_dir = dirname(dirname(__file__))
xunit_dir = join(test_dir, 'xunits')
xunit_xml = join(xunit_dir, 'results.xml')


class TestCases(unittest.TestCase):
    def setUp(self):
        chdir(dirname(__file__))

    def tearDown(self):
        pass

    def test_basic_parser(self):
        suite, result = parse(open(xunit_xml, encoding='utf-8'))
        assert isinstance(suite, unittest.TestSuite)
        assert isinstance(result, unittest.TestResult)

        passed = result.passed[0]
        print(passed)

        skipped = result.skipped[0]
        print(skipped)

        failure = result.failures[0]
        print(failure)

        error = result.errors
        assert len(error) == 0

        results = result.tests
        assert len(results) == 3

    def test_get_xml_by_pattern(self):
        print(realpath(curdir))
        files = get_files('../**/*.xml')
        assert len(files) == 2

        chdir(xunit_dir)
        print(realpath(curdir))
        files = get_files('*.xml')
        assert len(files) == 2

        files = get_files('re*.xml')
        assert len(files) == 1

        chdir(test_dir)
        print(realpath(curdir))
        files = get_files('*.xml')
        assert len(files) == 0

        files = get_files('**/*.xml')
        assert len(files) == 2

        chdir(dirname(test_dir))
        print(realpath(curdir))

        files = get_files('**/*.xml')
        assert len(files) == 2

    def test_parse_multiple_xml(self):
        files = get_files('../**/re*.xml')
        results, info = get_results(files)
        print(results)
        assert len(results) == 3
        print(info)
        assert len(info['files']) == 1
        assert info['duration'] == 0.069

        files = get_files('../**/*.xml')
        results, info = get_results(files)
        assert len(results) == 10
        print(info['start_time'], info['end_time'])
        assert info['start_time'] < info['end_time']
