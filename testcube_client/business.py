import arrow

from . import request_client as client
from .result_parser import get_results, get_files
from .settings import API, config, save_config, get_cache, add_cache

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


def run(result_xml_pattern, name=None, **kwargs):
    """One step to save a run with multiple xml files."""

    team = kwargs.pop('team')
    product = kwargs.pop('product')
    version = kwargs.pop('version', None)
    start_run(team_name=team, product_name=product,
              product_version=version, run_name=name,
              guess_start_time=True, **kwargs)

    finish_run(result_xml_pattern)


def start_run(team_name, product_name, product_version=None, run_name=None, **kwargs):
    """Will save current run id in config and return run url."""

    if not run_name:
        run_name = 'Tests running on {}'.format(config['host'])

    team_url = get_or_create_team(team_name)
    product_url = get_or_create_product(product_name, product_version)
    start_by = config['user']
    owner = kwargs.pop('owner', start_by)

    data = {'team': team_url, 'product': product_url,
            'start_by': start_by, 'owner': owner,
            'name': run_name, 'state': RunState.Starting}

    if not kwargs.pop('guess_start_time', False):
        data['start_time'] = arrow.utcnow().format()

    run = client.post(API.run, data=data)
    config['current_run'] = run
    save_config()
    print('Start new run: {}'.format(run['url']))
    return run['url']


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
    print('Finish run: {}'.format(run['url']))


def get_or_create_team(name):
    """return team url."""
    data = {'name': name}
    found = get_cache(API.team, **data)

    if found:
        return found['url']

    found = client.get(API.team, data)

    if found['count']:
        add_cache(API.team, found['results'][0])
        return found['results'][0]['url']
    else:
        team = client.post(API.team, data)
        add_cache(API.team, team)
        return team['url']


def update_team(name, owner):
    pass


def get_or_create_product(name, version='latest'):
    """return product url."""
    data = {'name': name}

    if version:
        data['version'] = version

    found = get_cache(API.product, **data)
    if found:
        return found['url']

    found = client.get(API.product, data)

    if found['count']:
        add_cache(API.product, found['results'][0])
        return found['results'][0]['url']
    else:
        product = client.post(API.product, data)
        add_cache(API.product, product)
        return product['url']


def get_or_create_testcase(name, full_name, team_url, product_url):
    """return testcase url."""
    data = {'name': name, 'full_name': full_name}

    found = get_cache(API.testcase, **data)
    if found:
        if found['team'] == team_url and found['product'] == product_url:
            return found['url']

    found = client.get(API.testcase, data)

    if found['count']:
        for tc in found['results']:
            if tc['team'] == team_url and tc['product'] == product_url:
                add_cache(API.testcase, tc)
                return tc['url']

    data['created_by'] = config['user']
    data['team'] = team_url
    data['product'] = product_url
    testcase = client.post(API.testcase, data)
    add_cache(API.testcase, testcase)
    return testcase['url']


def get_or_create_client(name=None):
    """return client url."""
    if not name:
        name = config['host']

    data = {'name': name}
    found = get_cache(API.client, **data)
    if found:
        return found['url']

    found = client.get(API.client, data)

    if found['count']:
        add_cache(API.client, found['results'][0])
        return found['results'][0]['url']
    else:
        c = client.post(API.client, data)
        add_cache(API.client, c)
        return c['url']


def create_result(run, result):
    """return result url."""
    name = result.methodname
    fullname = '{}.{}'.format(result.classname, result.methodname)

    testcase_url = get_or_create_testcase(name, fullname, run['team'], run['product'])
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
