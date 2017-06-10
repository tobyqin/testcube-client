from codecs import open
from os.path import realpath

import arrow
import glob2

from .utils.xunitparser import parse


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
    info = {'files': [], 'duration': 0, 'end_time': arrow.utcnow()}
    for xml in xml_files:
        with open_xml(xml) as f:
            info['files'].append({'name': xml, 'content': f.read()})

        suite, result = parse(open_xml(xml))
        info['duration'] += suite.time
        results.extend(getattr(result, 'tests'))

    info['start_time'] = info['end_time'].shift(seconds=-info['duration'])

    return results, info
