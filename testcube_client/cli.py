# -*- coding: utf-8 -*-

import argparse

from . import business
from .request_helper import register_client

parser = argparse.ArgumentParser(description="A Python client for testcube.")

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
        info = register_client(args.register)
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


#
# @click.command()
# @click.option('--start-run', '-s', help='Start a run.', is_flag=True)
# @click.option('--finish-run', '-f', help='Finish a run.', is_flag=True)
# @click.option('--run', '-r', help='Upload a run at one time.', is_flag=True)
# @click.option('--xunit-result', '-x', help='Specify the xunit xml results, e.g "**/result*.xml"')
# @click.option('--name', '-n', help='Specify the name.')
# @click.option('--team', '-t', help='Specify the team.')
# @click.option('--product', '-p', help='Specify the product.')
# @click.option('--product-version', '-v', help='Specify the product version. [Optional]')
# @click.option('--register', '-r', help='Register to the TestCube server, e.g. http://server:8000')
# def main(**kwargs):
#     """Console script for testcube_client"""
#     print(kwargs)


if __name__ == "__main__":
    main()
