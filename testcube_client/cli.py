# -*- coding: utf-8 -*-
"""

A Python client for testcube.

1. Register a testcube server::

  testcube-client --register http://server:8000

2.1 Start a test run::

  testcube-client --start-run -name "nightly run for testcube"  --team Core --product TestCube

2.2 Finish a test run with results, should --start-run first::

  testcube-client --finish-run --xunit-files "**/results/*.xml"

3. Start and finish run by one step::

  testcube-client --run -n "smoke tests for testcube" -t XPower -p TestCube -v v1.0 -x "**/smoke*.xml"

4. If your result will generate files, for example screenshots, then you can upload them as well.

  testcube-client --run -n "test run" -t Core -p TestCube -x "**/smoke*.xml" -i "**/out/*.png"

"""

import argparse
import logging

from . import business
from .request_helper import register_client
from .settings import enable_debug_log

parser = argparse.ArgumentParser(usage=__doc__)

# register & config
parser.add_argument('-r', '--register',
                    help='Register to the TestCube server, e.g. http://server:8000')
parser.add_argument('-f', '--force',
                    help='Force the action, support --register command.',
                    action='store_true')
parser.add_argument('-vb', '--verbose',
                    help='Show verbose log info.',
                    action='store_true')

# start / finish run
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
parser.add_argument('-i', '--result-files',
                    help='Specify the result files, e.g "**/output/**/*.png"')
parser.add_argument('-n', '--name',
                    help='Specify the run name.')
parser.add_argument('-t', '--team',
                    help='Specify the team name.')
parser.add_argument('-p', '--product',
                    help='Specify the product name.')
parser.add_argument('-v', '--product-version',
                    help='Specify the product version. [Optional]')

# handle reset tasks
parser.add_argument('-task', '--handle-task',
                    help='Handler pending task one by one.',
                    action='store_true')

# process reset task
parser.add_argument('-reset', '--reset-result',
                    help='Reset a result by reset_id, require xunit files.')

# clean up runs
parser.add_argument('-cleanup', '--cleanup-runs',
                    help='Cleanup old runs after specified days',
                    action='store_true')
parser.add_argument('-d', '--days',
                    help='Specify days when clean up old runs.')


def action(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
        return 0

    except Exception as e:
        logging.error('Action failed!!!')
        message = type(e).__name__ + ': ' + str(e)
        logging.error(message.decode('utf8') if hasattr(message, 'decode') else message)
        business.abort_run()
        raise e


def main():
    args = parser.parse_args()
    if args.verbose:
        enable_debug_log()

    # register should be first step
    if args.register:
        register_client(args.register, args.force)
        logging.info('Registration success! Please continue.')

    # batch create a test run: --run argument
    elif args.run:
        if args.start_run or args.finish_run:
            logging.error('Should not combine with --start-run or --finish-run argument!')
            return -1

        if not args.team or not args.product or not args.xunit_files:
            logging.error('Must specify --team, --product and --xunit-files!')
            return -1

        action(business.run,
               team_name=args.team,
               product_name=args.product,
               product_version=args.product_version,
               run_name=args.name,
               result_xml_pattern=args.xunit_files)

    # when only specify --start-run argument
    elif args.start_run:
        if args.run or args.finish_run:
            logging.error('Should not combine with --finish-run or --run argument!')
            return -1

        if not args.team or not args.product:
            logging.error('Must specify team and product!')
            return -1

        action(business.start_run,
               team_name=args.team,
               product_name=args.product,
               product_version=args.product_version,
               run_name=args.name)

    # when only specify --finish run argument
    elif args.finish_run:
        if args.run or args.start_run:
            logging.error('Should not combine with --start-run or --run argument!')
            return -1

        if not args.xunit_files:
            logging.error('Must specify --xunit-files!')
            return -1

        action(business.finish_run,
               result_xml_pattern=args.xunit_files)

    # when handle pending task
    elif args.handle_task:
        action(business.handle_task)

    # when reset a result
    elif args.reset_result:
        if not args.xunit_files:
            logging.error('Must specify --xunit-files!')
            return -1

        action(business.reset_result,
               reset_id=args.reset_result,
               result_xml_pattern=args.xunit_files)

    # when user need to upload result files: --result-files
    if args.result_files:
        action(business.upload_files, file_patterns=args.result_files)

    # when user clean up old runs
    if args.cleanup_runs:
        if not args.days:
            logging.error('Must specify --days!')
            return -1
        action(business.cleanup_runs,
               days=args.days)


if __name__ == "__main__":
    main()
