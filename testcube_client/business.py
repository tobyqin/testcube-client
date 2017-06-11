import testcube_client.testcube_client as client
from testcube_client.result_parser import get_results, get_files
from testcube_client.settings import API, config


def run(result_xml_pattern, name=None, **kwargs):
    """One step to save a run with multiple xml files."""
    team = kwargs.pop('team')
    product = kwargs.pop('product')
    version = kwargs.pop('version', None)
    start_run(team=team, product=product, version=version, name=name, **kwargs)
    finish_run(result_xml_pattern)


def start_run(team, product, version=None, name=None, **kwargs):
    """Will save current run id in config and print out."""
    if not name:
        name = 'Tests running on {}'.format(config['host'])

    team = get_or_create_team(team)
    product = get_or_create_product(product, version)
    start_by = config['user']
    owner = kwargs.pop('owner', start_by)

    data = {'team': team, 'product': product, 'start_by': start_by, 'owner': owner}
    run = client.post(API.run, data=data)
    config['current_run'] = run
    print('Start new run: {}'.format(run['url']))


def finish_run(result_xml_pattern, run=None):
    """Follow up step to save run info after starting a run."""
    files = get_files(result_xml_pattern)
    results, info = get_results(files)

    if not run:
        assert 'current_run' in config, 'Seems like you never start a run!'
        run = config['current_run']

    for result in results:
        update_or_create_result(run, result=result)

    data = {'start_time': info['start_time'], 'end_time': info['end_time']}
    client.put(run['url'], data)
    print('Finish run: {}'.format(run['url']))


def get_or_create_team(name):
    data = {'name': name}
    found = client.get(API.team, data)

    if found['count']:
        return found['results'][0]['url']
    else:
        return client.post(API.team, data)['url']


def update_team(name, owner):
    pass


def get_or_create_product(name, version=None):
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
    if not name:
        name = config['host']

    data = {'name': name}

    found = client.get(API.client, data)

    if found['count']:
        return found['results'][0]['url']
    else:
        return client.post(API.client, data)['url']


def update_or_create_result(run, result):
    name = result.methodname
    fullname = '{}.{}'.format(result.classname, result.methodname)

    team = client.get_obj(run['team'])
    product = client.get_obj(run['product'])

    testcase_url = get_or_create_testcase(name, fullname, team['url'], product['url'])
    client_url = get_or_create_client()
    duration = result.time.total_seconds()
    outcome = 0
    stdout = result.stdout
    stderr = result.stderr

    if result.result == 'failure':
        outcome = 1
        message = result.message
        stacktrace = result.alltext

    data = {'test_run': run['url'], 'testcase': testcase_url,
            'duration': duration, 'outcome': outcome,
            'assigned_to': run['owner'], 'test_client': client_url}

    r = client.post(API.result, data=data)
    return r['url']
