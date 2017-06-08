import requests
import uuid
import socket
import getpass


def register_client(server_url):
    token = 'testcube_client_{}'.format(uuid.uuid4())
    client_name = socket.gethostname()
    username = getpass.getuser()

    data = {'token': token,
            'client_name': client_name,
            'client_user': username}

    assert isinstance(server_url, str)

    if not server_url.endswith('/'):
        server_url += '/'

    register_url = server_url + 'client-register'
    response = requests.post(register_url, data=data)

    assert response.status_code == 200, 'Failed to register client, response: ' + response.text
    return response.json()
