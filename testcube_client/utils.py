import logging
from os import environ

from .settings import config


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
