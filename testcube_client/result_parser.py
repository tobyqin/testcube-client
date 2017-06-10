from codecs import open

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

    return glob2.glob(pattern)


def open_xml(file):
    return open(file)


def get_suite(xml):
    suite, _ = parse(open_xml(xml))
    return suite


def get_result(xml):
    _, result = parse(open_xml(xml))
    return result
