import arrow

from . import request_client as client
from .result_parser import get_results, get_files
from .settings import API, save_config, get_cache, add_cache
from .utils import *

outcome_map = {'success': 0,
               'failure': 1,
               'skipped': 2,
               'error': 3}


class RunState:
    NotReady = -1
    Starting = 0
    Running = 1
    Aborted = 2
    Completed = 3


class RunStatus:
    Pending = -1
    Passed = 0
    Failed = 1
    Analyzed = 2
    Abandoned = 3


@log_params
def run(result_xml_pattern, name=None, **kwargs):
    """One step to save a run with multiple xml files."""

    start_run(**kwargs)
    finish_run(result_xml_pattern=result_xml_pattern, guess_start_time=True)


@log_params
def start_run(team_name, product_name, product_version=None, run_name=None, **kwargs):
    """Will save current run id in config and return run url."""

    if not run_name:
        run_name = get_default_run_name()

    team_url = get_or_create_team(team_name)
    product_url = get_or_create_product(product_name, team_url, product_version)
    start_by = config['user']
    owner = kwargs.pop('owner', config['current_product']['owner']) or start_by

    data = {'product': product_url,
            'start_by': start_by, 'owner': owner,
            'name': run_name, 'state': RunState.Starting}

    if not kwargs.pop('guess_start_time', False):
        data['start_time'] = arrow.utcnow().format()

    run = client.post(API.run, data=data)
    config['current_run'] = run
    save_config()
    logging.info('Start new run: {}'.format(get_run_url(run)))

    add_run_source(run['url'])
    return run['url']


@log_params
def abort_run(run=None):
    if not run:
        assert 'current_run' in config, 'Seems like you never start a run!'
        run = config['current_run']

    data = {'status': RunStatus.Abandoned, 'state': RunState.Aborted}
    run = client.patch(run['url'], data)
    config['current_run'] = run
    save_config()
    logging.warning('Abandon run: {}'.format(run['url']))


@log_params
def finish_run(result_xml_pattern, run=None, **kwargs):
    """Follow up step to save run info after starting a run."""
    files = get_files(result_xml_pattern)
    results, info = get_results(files)

    if not run:
        assert 'current_run' in config, 'Seems like you never start a run!'
        run = config['current_run']

    for result in results:
        create_result(run, result=result)

    data = {'end_time': info['end_time'], 'status': RunStatus.Failed, 'state': RunState.Completed}

    if kwargs.pop('guess_start_time', False):
        data['start_time'] = info['start_time']

    if info['passed']:
        data['status'] = RunStatus.Passed

    run = client.patch(run['url'], data)
    config['current_run'] = run
    save_config()
    logging.info('Finish run: {}'.format(get_run_url(run)))


def get_or_create_object(api_url, data, fix_fields=None, extra_data=None):
    fields = {}
    found = get_cache(api_url, **data)

    if found:  # search from cache
        return found

    if fix_fields:  # convert instance url to id when get from server
        for f in fix_fields:
            fields[f] = (data[f], get_object_id(data[f]))
            data[f] = fields[f][1]

    found = client.get(api_url, data)

    if found['count']:  # search from server
        add_cache(api_url, found['results'][0])
        return found['results'][0]


    else:  # create a new object

        if fix_fields:  # use instance url to create the object
            for f in fix_fields:
                data[f] = fields[f][0]

        if extra_data:  # extra fields required
            data.update(extra_data)

        object = client.post(api_url, data)
        add_cache(api_url, object)
        return object


@as_config('current_team', 'url')
def get_or_create_team(name):
    """return team url."""
    data = {'name': name}
    return get_or_create_object(API.team, data,
                                extra_data={'owner': config['user']})


@as_config('current_product', 'url')
def get_or_create_product(name, team_url, version='latest'):
    """return product url."""
    data = {'name': name, 'team': team_url}

    team = get_cache(API.team, url=team_url)
    if not team:
        team = client.get_obj(team_url)

    if version:
        data['version'] = version

    return get_or_create_object(API.product, data,
                                fix_fields=['team'],
                                extra_data={'owner': team['owner'] or config['user']})


def get_or_create_testcase(name, full_name, product_url):
    """return testcase url."""
    data = {'name': name, 'full_name': full_name, 'product': product_url}

    product = get_cache(API.product, url=product_url)
    if not product:
        product = client.get_obj(product_url)

    owner = product['owner'] or config['user']
    return get_or_create_object(API.testcase, data,
                                fix_fields=['product'],
                                extra_data={'created_by': config['user'], 'owner': owner})['url']


def get_or_create_client(name=None):
    """return client url."""
    data = {'name': name or config['host']}
    return get_or_create_object(API.client, data)['url']


def create_result(run, result):
    """return result url."""
    name = result.methodname
    fullname = '{}.{}'.format(result.classname, result.methodname)

    testcase_url = get_or_create_testcase(name, fullname, run['product'])
    client_url = get_or_create_client()
    duration = result.time.total_seconds()
    outcome = outcome_map[result.result]
    stdout = result.stdout

    data = {'test_run': run['url'], 'testcase': testcase_url,
            'duration': duration, 'outcome': outcome,
            'assigned_to': run['owner'], 'test_client': client_url,
            'stdout': stdout}

    # success / skipped / error / failure
    if result.result in ('failure', 'error'):

        error_info = {'stdout': result.stdout,
                      'stderr': result.stderr,
                      'message': result.message,
                      'stacktrace': result.trace,
                      'exception_type': 'UnDetermined'
                      }

        if getattr(result, 'failureException'):
            error_info['exception_type'] = result.failureException.__name__

        error_url = create_error(error_info)
        data['error'] = error_url

    elif result.result == 'skipped':
        data['stdout'] = result.alltext

    result_obj = client.post(API.result, data=data)
    return result_obj['url']


def create_error(error_info):
    err = client.post(API.error, error_info)
    return err['url']


def rerun_result(old_result_id, result):
    pass


def add_run_source(run_url):
    link, name = get_run_source()
    if link:
        data = {'link': link, 'run': run_url, 'name': name}
        source = client.post(API.run_source, data=data)
        return source['url']
