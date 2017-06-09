import glob2
import xunitparser


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


def get_suite(xml):
    suite, _ = xunitparser.parse(open(xml))
    return suite


def get_result(xml):
    _, result = xunitparser.parse(open(xml))
    return result
