import getpass
import json
import logging
import platform
import socket
import sys
from codecs import open
from os.path import exists, join, expanduser

config = {'cache': []}

home_dir = expanduser('~')
config_file = join(home_dir, '.testcube_client.json')
logging.basicConfig(stream=sys.stdout,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.INFO)


def enable_debug_log():
    logging.root.setLevel(logging.DEBUG)


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
    """example: get_cache(type='User', name='Toby', age=18)"""
    filters['__type__'] = type
    matched = []
    for c in config['cache']:
        c = c.copy()  # copy it for return  to avoid user update the cached object.

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


# always load config when app start (import happens)
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
    object_source = 'object_sources'
    result_file = 'result_files'
    reset_result = 'reset_results'
    task = 'tasks'
    run_variable = 'run_variables'
