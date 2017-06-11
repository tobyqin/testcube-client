import arrow

import testcube_client.testcube_client as client
from testcube_client.result_parser import get_results, get_files
from testcube_client.settings import API, config

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
    print('Finish run: {}'.format(run['url']))


def get_or_create_team(name):
    """return team url."""
    data = {'name': name}
    found = client.get(API.team, data)

    if found['count']:
        return found['results'][0]['url']
    else:
        return client.post(API.team, data)['url']


def update_team(name, owner):
    pass


def get_or_create_product(name, version=None):
    """return product url."""
    data = {'name': name}

    if version:
        data['version'] = version

    found = client.get(API.product, data)

    if found['count']:
        return found['results'][0]['url']
    else:
        return client.post(API.product, data)['url']


def add_product(name, version):
    pass


def get_or_create_testcase(name, full_name, team_url, product_url):
    """return testcase url."""
    data = {'name': name, 'full_name': full_name}

    found = client.get(API.testcase, data)

    if found['count']:
        for tc in found['results']:
            if tc['team'] == team_url and tc['product'] == product_url:
                return tc['url']

    data['created_by'] = config['user']
    data['team'] = team_url
    data['product'] = product_url
    return client.post(API.testcase, data)['url']


def get_or_create_client(name=None):
    """return client url."""
    if not name:
        name = config['host']

    data = {'name': name}

    found = client.get(API.client, data)

    if found['count']:
        return found['results'][0]['url']
    else:
        return client.post(API.client, data)['url']


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
