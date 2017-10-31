import json
import logging
from os import environ
from os.path import basename, getsize, getmtime, splitext, exists

import arrow

from .settings import config


def env_to_json():
    """convert current env variables to json text."""
    return json.dumps(dict(environ))


def get_default_run_name():
    """try to get run name for jenkins job."""
    run_name = 'Tests running on {}'.format(config['host'])
    return environ.get('JOB_NAME', run_name)


def get_run_source():
    """try to get run source link and name."""
    name = 'Jenkins' if environ.get('JENKINS_HOME', None) else 'Build'
    link = environ.get('BUILD_URL', None)
    return link, name


def get_object_id(object_url):
    """ 'http://.../api/run/123/' => 123"""
    url = object_url[:-1]
    return int(url[url.rindex('/') + 1:])


def get_run_url(run_obj):
    """ 'http://../api/runs/123/' => http://.../runs/123"""
    return run_obj['url'].replace('api/', '')[0:-1]


def get_result_url(result_obj):
    """same logic to get result rul."""
    return get_run_url(result_obj)


def log_params(func):
    """decorator to debug a function params"""

    def wrapper(*args, **kwargs):
        logging.debug("{}(): args={}, kwargs={}".format(func.__name__, args, kwargs))
        return func(*args, **kwargs)

    return wrapper


def as_config(name, return_field=None):
    """decorator to save function result as config"""

    def wrapper(func):
        def _wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            config[name] = result
            return result[return_field] if return_field else result

        return _wrapper

    return wrapper


def get_file_info(file_path):
    valid_file_types = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.txt', '.log', '.csv']
    if not exists(file_path):
        logging.error('File not found: {}'.format(file_path))

    elif splitext(file_path)[1].lower() not in valid_file_types:
        logging.error('Invalid file type: {}'.format(splitext(file_path)[1]))

    elif getsize(file_path) == 0:
        logging.error('File is empty: {}'.format(file_path))

    else:
        return {'name': basename(file_path),
                'file_byte_size': getsize(file_path),
                'file_created_time': str(arrow.get(getmtime(file_path)))}
