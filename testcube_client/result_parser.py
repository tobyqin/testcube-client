from codecs import open

import glob2

from .utils.xunitparser import parse
from os.path import realpath


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


def get_suite(xml):
    suite, _ = parse(open_xml(xml))
    return suite


def get_results(xml_files):
    """return a list of test results for multiple xml files"""
    results = []
    for xml in xml_files:
        _, result = parse(open_xml(xml))
        results.extend(getattr(result, 'tests'))

    return results
