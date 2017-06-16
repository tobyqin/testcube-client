import getpass
import json
import platform
import socket
from codecs import open
from os.path import exists, join, expanduser

config = {'cache': []}

home_dir = expanduser('~')
config_file = join(home_dir, '.testcube_client.json')


def add_cache(type, obj):
    if isinstance(obj, list):
        for i in obj:
            add_cache(type, i)

    elif isinstance(obj, dict):
        obj['__type__'] = type

        if get_cache(type, **obj):
            return

        config['cache'].append(obj)
        save_config()

    else:
        raise ValueError('Not support caching: {}!'.format(obj))


def get_cache(type, expected_one=True, **filters):
    """example: get_cache(type='User', name='Toby',age=18)"""
    filters['__type__'] = type
    matched = []
    for c in config['cache']:
        c = c.copy()
        success = []
        for k, v in filters.items():
            success.append(c.get(k, None) == v)

        if all(success):
            matched.append(c)

    if expected_one:
        if len(matched) > 1:
            raise ValueError("Multiple cache hit! {}".format(filters))

        return matched[0] if matched else None

    else:
        return matched


def delete_cache(type, **filters):
    """example: delete_cache(type='User', name='Toby',age=18)"""
    filters['__type__'] = type
    not_matched = []
    for c in config['cache']:
        success = []
        for k, v in filters.items():
            success.append(c.get(k, None) == v)

        if not all(success):
            not_matched.append(c)

    config['cache'] = not_matched
    save_config()


def load_config():
    if exists(config_file):
        with open(config_file, encoding='utf-8') as f:
            content = f.read()
            if content:
                config.update(json.loads(content))

    config['host'] = socket.gethostname()
    config['user'] = getpass.getuser()
    config['platform'] = '{} {}'.format(platform.platform(), platform.machine())


def save_config():
    with open(config_file, mode='w', encoding='utf-8') as f:
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
