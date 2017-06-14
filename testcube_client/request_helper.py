import requests

from .settings import config, save_config


def register_client(server_url, force=False):
    if 'token' in config and not force:
        print('Already register to: {}'.format(config['server']))
        return {'client': config['client'], 'token': config['token']}

    client_type = 'testcube_python_client'

    data = {'client_type': client_type,
            'client_name': config['host'],
            'client_user': config['user'],
            'platform': config['platform']}

    assert isinstance(server_url, str)

    if not server_url.endswith('/'):
        server_url += '/'

    register_url = server_url + 'client-register'
    response = requests.post(register_url, data=data)
    assert response.status_code == 200, 'Failed to register client, response: ' + response.text

    info = response.json()

    config['server'] = server_url
    config.update(info)
    config['cache'] = []
    config.pop('current_run', None)

    save_config()
    print('Register to: {}'.format(config['server']))
    return info


def api_url(endpoint):
    if 'server' not in config:
        raise EnvironmentError('Must register a testcube server!')

    return '{}api/{}/'.format(config['server'], endpoint)


def api_auth():
    return (config['client'], config['token'])


def api_result(response, as_json=True):
    if response.status_code not in (200, 201, 204, 205):
        raise ValueError('[{} {}]: {}'.format(response.request.method,
                                              response.url,
                                              response.text))

    if as_json:
        try:
            return response.json()
        except ValueError:
            return obj_moved(response)
    else:
        return response.text


def obj_moved(response):
    """
    It might returns Document Moved page on IIS server.
    https://forums.iis.net/p/1209573/2073536.aspx?IIS+7+5+adding+Document+Moved+content+when+Location+header+is+present
    """
    if response.url != response.headers['location']:
        return requests.get(response.headers['location']).json()
    else:
        raise ValueError("Expected json response at {} [{}]: {}"
                         .format(response.url, response.request.method, response.text))
