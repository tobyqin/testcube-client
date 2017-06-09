import requests

from .settings import config, save_config


def register_client(server_url):
    client_type = 'testcube_python_client'

    data = {'client_type': client_type,
            'client_name': config['host'],
            'client_user': config['user']}

    assert isinstance(server_url, str)

    if not server_url.endswith('/'):
        server_url += '/'

    register_url = server_url + 'client-register'
    response = requests.post(register_url, data=data)
    assert response.status_code == 200, 'Failed to register client, response: ' + response.text

    info = response.json()
    config['server'] = server_url
    config['client'] = info['username']
    config['token'] = info['password']
    save_config()

    return info
