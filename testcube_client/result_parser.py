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

    files = [realpath(p) for p in glob2.glob(pattern)]
    return list(set(files))


def open_xml(file):
    return open(file, encoding='utf-8')


def read_file(file):
    try:
        with open(file, encoding='utf-8') as f:
            return f.read
    except UnicodeDecodeError as e:
        return 'Failed to open file: {}: {}'.format(file, str(e))


def get_results(xml_files):
    """return a list of test results and info dict for multiple xml files"""
    results = []
    info = {'files': [], 'duration': 0, 'end_time': arrow.utcnow(), 'passed': True}

    for xml in xml_files:
        info['files'].append({'name': xml, 'content': read_file(xml)})
        suite, result = parse(xml)

        results.extend(getattr(result, 'tests'))

        if len(result.tests) != len(result.passed) + len(result.skipped):
            info['passed'] = False

    # sum the time from testcase

    for test in results:
        info['duration'] += test.time.total_seconds()

    info['start_time'] = info['end_time'].shift(seconds=-info['duration'])
    info['start_time'] = info['start_time'].format()
    info['end_time'] = info['end_time'].format()

    return results, info
