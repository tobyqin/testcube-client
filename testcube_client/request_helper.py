import re

import requests

from .settings import config, save_config


def register_client(server_url):
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
    save_config()

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
    """It might returns Document Moved page on some python version."""
    pattern = r'<a HREF="(.*)">here<\/a>'
    match = re.search(pattern, response.text)
    if match:
        return requests.get(match.group(1)).json()
    else:
        raise ValueError("Expected json response at {} [{}]: {}"
                         .format(response.url, response.request.method, response.text))
