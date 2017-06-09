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
            c = json.loads(f.read())
            for k, v in c.items():
                config[k] = v

    config['host'] = socket.gethostname()
    config['user'] = getpass.getuser()
    config['platform'] = '{} {}'.format(platform.platform(), platform.machine())


def save_config():
    if exists(config_file):
        print("Warning: overwrite existed config file: {}".format(config_file))

    with open(config_file, 'w') as f:
        f.write(json.dumps(config))


load_config()
