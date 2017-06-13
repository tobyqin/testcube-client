from codecs import open
from os.path import realpath

import arrow
import glob2

from .xunitparser import parse


def get_files(pattern):
    """
    Get all files match glob pattern.

    Examples:
      *.xml
      **/*.xml
      result*.xml
      result/smoke*.xml

    :param pattern: glob patterns https://pypi.python.org/pypi/glob2
    :return:matched files
    """

    return [realpath(p) for p in glob2.glob(pattern)]


def open_xml(file):
    return open(file, encoding='utf-8')


def get_results(xml_files):
    """return a list of test results and info dict for multiple xml files"""
    results = []
    info = {'files': [], 'duration': 0, 'end_time': arrow.utcnow(), 'passed': True}
    time_from_suite = True

    for xml in xml_files:
        with open_xml(xml) as f:
            info['files'].append({'name': xml, 'content': f.read()})

        suite, result = parse(xml)

        # expect there is a time attribute in suite node
        time_from_suite = time_from_suite and suite.time

        if time_from_suite:
            info['duration'] += suite.time

        results.extend(getattr(result, 'tests'))
        passed = len(result.tests) == len(result.passed) + len(result.skipped)
        info['passed'] = info['passed'] and passed

    # sum the time from testcase if no time in suite
    if not time_from_suite:
        for test in results:
            info['duration'] += test.time.total_seconds()

    info['start_time'] = info['end_time'].shift(seconds=-info['duration'])
    info['start_time'] = info['start_time'].format()
    info['end_time'] = info['end_time'].format()

    return results, info
