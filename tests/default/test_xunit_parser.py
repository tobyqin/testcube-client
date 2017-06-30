import logging
import unittest
from os import chdir
from os.path import dirname, join, curdir, realpath

from testcube_client.result_parser import get_files, get_results
from testcube_client.settings import enable_debug_log
from testcube_client.xunitparser import parse

test_dir = dirname(dirname(__file__))
xunit_dir = join(test_dir, 'xunits')
xunit_xml = join(xunit_dir, 'results.xml')


class TestCases(unittest.TestCase):
    def setUp(self):
        enable_debug_log()

    def tearDown(self):
        pass

    def test_basic_parser(self):
        suite, result = parse(xunit_xml)
        assert isinstance(suite, unittest.TestSuite)
        assert isinstance(result, unittest.TestResult)

        passed = result.passed[0]
        logging.info(passed)

        skipped = result.skipped[0]
        logging.info(skipped)

        failure = result.failures[0]
        logging.info(failure)

        error = result.errors
        assert len(error) == 0

        results = result.tests
        assert len(results) == 3

    def test_get_xml_by_pattern(self):
        chdir(dirname(__file__))
        logging.info(realpath(curdir))
        files = get_files('../**/*.xml')
        assert len(files) == 2

        chdir(xunit_dir)
        logging.info(realpath(curdir))
        files = get_files('*.xml')
        assert len(files) == 2

        files = get_files('re*.xml')
        assert len(files) == 1

        chdir(test_dir)
        logging.info(realpath(curdir))
        files = get_files('*.xml')
        assert len(files) == 0

        files = get_files('**/*.xml')
        assert len(files) == 2

        chdir(dirname(test_dir))
        logging.info(realpath(curdir))

        files = get_files('**/*.xml')
        assert len(files) == 2

    def test_parse_multiple_xml(self):
        chdir(dirname(__file__))
        files = get_files('../**/re*.xml')
        results, info = get_results(files)
        logging.info(results)
        assert len(results) == 3
        logging.info(info)
        assert len(info['files']) == 1
        assert info['duration'] > 0

        files = get_files('../**/*.xml')
        results, info = get_results(files)
        assert len(results) == 10
        logging.info('%s, %s', info['start_time'], info['end_time'])
        assert info['start_time'] < info['end_time']


if __name__ == '__main__':
    unittest.main()
