# -*- coding: utf-8 -*-
"""

A Python client for testcube.

1. Register a testcube server::

  testcube-client --register http://server:8000

2.1 Start a test run::

  testcube-client --start-run -name "nightly run for testcube"  --team Core --product TestCube

2.2 Finish a test run with results, should --start-run first::

  testcube-client --finish-run --xunit-files **/results/*.xml

3. Start and finish run by one step::

  testcube-client --run -n "smoke tests for testcube" -t XPower -p TestCube -v v1.0 -x **/smoke*.xml

"""

import argparse

from . import business
from .request_helper import register_client

parser = argparse.ArgumentParser(usage=__doc__)

parser.add_argument('-r', '--register',
                    help='Register to the TestCube server, e.g. http://server:8000')
parser.add_argument('-run', '--run',
                    help='Upload run info at one time, require team,product,name and xunit files.',
                    action='store_true')
parser.add_argument('-start', '--start-run',
                    help='Start a run, require team, product and a name.',
                    action='store_true')
parser.add_argument('-finish', '--finish-run',
                    help='Finish a run, require xunit files.',
                    action='store_true')
parser.add_argument('-x', '--xunit-files',
                    help='Specify the xunit xml results, e.g "**/result*.xml"')
parser.add_argument('-n', '--name',
                    help='Specify the run name.')
parser.add_argument('-t', '--team',
                    help='Specify the team name.')
parser.add_argument('-p', '--product',
                    help='Specify the product name.')
parser.add_argument('-v', '--product-version',
                    help='Specify the product version. [Optional]')
parser.add_argument('-f', '--force',
                    help='Force the action, support --register command.',
                    action='store_true')


def action(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
        return 0

    except Exception as e:
        print('Action failed!!!')
        print(type(e).__name__ + ': ' + ','.join(e.args))
        raise e


def main():
    args = parser.parse_args()
    if args.register:
        info = register_client(args.register, args.force)
        print('Registration success! Please continue other actions. <{}>'.format(info['token']))
    elif args.run:
        if args.start_run or args.finish_run:
            print('Should not combine with --start-run or --finish-run argument!')
            return -1

        if not args.team or not args.product or not args.xunit_files:
            print('Must specify --team, --product and --xunit-files!')
            return -1

        action(business.run,
               team=args.team,
               product=args.product,
               version=args.product_version,
               name=args.name,
               result_xml_pattern=args.xunit_files)


    elif args.start_run:
        if args.run or args.finish_run:
            print('Should not combine with --finish-run or --run argument!')
            return -1

        if not args.team or not args.product:
            print('Must specify team and product!')
            return -1

        action(business.start_run,
               team_name=args.team,
               product_name=args.product,
               product_version=args.product_version,
               run_name=args.name)

    elif args.finish_run:
        if args.run or args.start_run:
            print('Should not combine with --start-run or --run argument!')
            return -1

        if not args.xunit_files:
            print('Must specify --xunit-files!')
            return -1

        action(business.finish_run,
               result_xml_pattern=args.xunit_files)


if __name__ == "__main__":
    main()
