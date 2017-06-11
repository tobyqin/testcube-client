# -*- coding: utf-8 -*-

import argparse

import click

# from testcube_client.request_helper import register_client
# from testcube_client import business

parser = argparse.ArgumentParser(description="A Python client for testcube.")

parser.add_argument('-g', '--register',
                    help='Register to the TestCube server, e.g. http://server:8000')
parser.add_argument('-r', '--run',
                    help='Upload run info at one time, require team,product,name and xunit files.',
                    action='store_true')
parser.add_argument('-s', '--start-run',
                    help='Start a run, require team, product and a name.',
                    action='store_true')
parser.add_argument('-f', '--finish-run',
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


def entry():
    args = parser.parse_args()
    print(args)


@click.command()
@click.option('--start-run', '-s', help='Start a run.', is_flag=True)
@click.option('--finish-run', '-f', help='Finish a run.', is_flag=True)
@click.option('--run', '-r', help='Upload a run at one time.', is_flag=True)
@click.option('--xunit-result', '-x', help='Specify the xunit xml results, e.g "**/result*.xml"')
@click.option('--name', '-n', help='Specify the name.')
@click.option('--team', '-t', help='Specify the team.')
@click.option('--product', '-p', help='Specify the product.')
@click.option('--product-version', '-v', help='Specify the product version. [Optional]')
@click.option('--register', '-r', help='Register to the TestCube server, e.g. http://server:8000')
def main(**kwargs):
    """Console script for testcube_client"""
    print(kwargs)


if __name__ == "__main__":
    entry()
