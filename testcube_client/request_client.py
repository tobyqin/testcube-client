# -*- coding: utf-8 -*-
import logging

import requests

from .request_helper import api_auth, api_result, api_url


def get(api_endpoint, params=None):
    """get, params is a dict which will be converted to query string."""
    logging.debug('get {}: {}'.format(api_endpoint, params))
    response = requests.get(api_url(api_endpoint), params=params)
    return api_result(response)


def get_obj(obj_url):
    logging.debug('get object: {}'.format(obj_url))
    response = requests.get(obj_url)
    return api_result(response)


def post(api_endpoint, data):
    """create to list view"""
    logging.debug('post {}: {}'.format(api_endpoint, data))
    response = requests.post(api_url(api_endpoint), data=data, auth=api_auth())
    return api_result(response)


def patch(obj_url, data):
    """patch an object with partial data"""
    logging.debug('patch {}: {}'.format(obj_url, data))
    response = requests.patch(obj_url, data=data, auth=api_auth())
    return api_result(response)


def delete(object_url):
    """delete to object instance"""
    logging.debug('delete {}'.format(object_url))
    response = requests.delete(object_url, auth=api_auth())
    return api_result(response, as_json=False)


def put(obj_url, data):
    """update to object instance"""
    logging.debug('put {}: {}'.format(obj_url, data))
    response = requests.put(obj_url, data=data, auth=api_auth())
    return api_result(response)
