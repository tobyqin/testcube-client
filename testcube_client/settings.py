import getpass
import json
import socket
from os.path import exists, join, expanduser
import platform

config = {}

home_dir = expanduser('~')
config_file = join(home_dir, '.testcube_client.json')


def load_config():
    if exists(config_file):
        with open(config_file) as f:
            content = f.read()
            if content:
                config.update(json.loads(content))

    config['host'] = socket.gethostname()
    config['user'] = getpass.getuser()
    config['platform'] = '{} {}'.format(platform.platform(), platform.machine())


def save_config():
    with open(config_file, 'w') as f:
        f.write(json.dumps(config, indent=4))


load_config()


class API:
    team = 'teams'
    product = 'products'
    run = 'runs'
    result = 'results'
    testcase = 'cases'
    client = 'clients'
    issue = 'issues'
    analysis = 'analysis'
    error = 'errors'
