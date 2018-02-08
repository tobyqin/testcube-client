import requests

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
    save_env_variable(run['url'])

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
    data = generate_result_data(result, testcase_url)
    data['test_run'], data['assigned_to'] = run['url'], run['owner']

    result_obj = client.post(API.result, data=data)
    return result_obj['url']


def generate_result_data(xml_result_obj, test_case_url, add_new_error=True):
    """generate result data in one place."""
    duration = xml_result_obj.time.total_seconds()
    outcome = outcome_map[xml_result_obj.result]
    stdout = xml_result_obj.stdout

    data = {'testcase': test_case_url,
            'duration': duration,
            'outcome': outcome,
            'test_client': get_or_create_client(),
            'stdout': stdout}

    # success / skipped / error / failure
    if xml_result_obj.result in ('failure', 'error'):

        error_info = {'stdout': xml_result_obj.stdout,
                      'stderr': xml_result_obj.stderr,
                      'message': xml_result_obj.message,
                      'stacktrace': xml_result_obj.trace,
                      'exception_type': 'Undetermined'
                      }

        if getattr(xml_result_obj, 'failureException'):
            error_info['exception_type'] = xml_result_obj.failureException.__name__

        if add_new_error:
            error_url = create_error(error_info)
            data['error'] = error_url
        else:
            data.update(error_info)

    elif xml_result_obj.result == 'skipped':
        data['stdout'] = xml_result_obj.alltext

    return data


def create_error(error_info):
    err = client.post(API.error, error_info)
    return err['url']


@log_params
def reset_result(reset_id, result_xml_pattern):
    """
    reset a result by reset id and xml file pattern.
    1. get result id by reset object
    2. get testcase name from result object
    3. search testcase from provided xml results
    4. upload matched result to reset object
    """
    logging.info("Reset result by reset id: {}".format(reset_id))

    reset_url = '{}api/{}/{}/'.format(config['server'], API.reset_result, reset_id)
    reset = client.get_obj(reset_url)
    result = client.get_obj(reset['origin_result'])
    run = client.get_obj(result['test_run'])
    case = client.get_obj(result['testcase'])

    logging.info("Original Result: {}".format(get_result_url(result)))

    # save result run as current run, so user can upload images to correct run
    config['current_run'] = run
    save_config()

    files = get_files(result_xml_pattern)
    found = [r for r in get_results(files)[0] if r.methodname == case['name']]

    if found:
        data = generate_result_data(xml_result_obj=found[0],
                                    test_case_url=result['testcase'],
                                    add_new_error=False)

        data['run_on'] = arrow.utcnow().format()
        data['test_client'] = get_object_id(data['test_client'])

        handler_url = '{}/{}/handler'.format(API.reset_result, get_object_id(reset['url']))
        response = client.post(handler_url, data=data)
        logging.info(response)
        logging.info('Done.')
        return

    logging.warning("No matched result file found.")


def add_run_source(run_url):
    link, name = get_run_source()
    if link:
        # create the source object
        data = {'link': link, 'name': name}
        source = client.post(API.object_source, data=data)

        # link the source to a run
        data = {'source': source['url']}
        client.patch(run_url, data)

        return source['url']


def upload_files(file_patterns):
    run = config.get('current_run')
    if not run:
        raise RuntimeError('Should start a run at first!')

    for file in get_files(file_patterns):
        upload_result_file(file, run['url'])


def upload_result_file(file_path, run_url):
    """to upload single result file."""
    data = get_file_info(file_path)
    if data:
        data['run'] = run_url
        files = {'file': open(file_path, 'rb')}
        file = client.post(API.result_file, data=data, files=files)
        logging.info('File uploaded: {}'.format(file_path))
        return file['url']
    else:
        logging.warning('File skipped: {}'.format(file_path))


def handle_task():
    """get and handle pending task one by one."""
    pending_task_api = '{}api/{}/pending'.format(config['server'], API.task)
    pending_task = client.get_obj(pending_task_api)

    if not pending_task:
        logging.info('No pending task found, goodbye.')
        return

    logging.info('Found pending task: {}, data: {}'.format(
        pending_task['description'], pending_task['data']))

    logging.info('Process command: {}'.format(pending_task['command']))
    data = {'status': 'Sent'}

    try:
        response = requests.get(pending_task['command'])

        if response.status_code < 200 or response.status_code > 210:
            data['message'] = response.text

    except Exception as e:
        logging.exception('Failed to process task!')
        data['status'] = 'Error'
        data['message'] = '{}: {}'.format(type(e).__name__, e.args)

    logging.info('Upload data: {}'.format(data))
    task_handler_api = '{}/{}/handler'.format(API.task, get_object_id(pending_task['url']))
    client.post(task_handler_api, data=data)


def save_env_variable(run_url):
    """save current env variables as run extra data."""

    data = {'test_run': run_url, 'data': env_to_json()}
    var = client.post(API.run_variable, data=data)

    return var['url']


def cleanup_runs(days):
    """clean up old runs after specified days."""
    logging.info('Cleanup runs {} days ago...'.format(days))
    data = {'days': days}
    result = client.get(API.run + '/cleanup', params=data)
    logging.info('Runs had been cleaned up: {}'.format(result))
