# -*- coding: utf-8 -*-
import requests
from .request_helper import api_auth, api_result, api_url


def get(api_endpoint, params):
    """get, params is a dict which will be converted to query string."""
    response = requests.get(api_url(api_endpoint), params=params, auth=api_auth())
    return api_result(response)


def post(api_endpoint, data):
    """create to list view"""
    response = requests.post(api_url(api_endpoint), data=data, auth=api_auth())
    return api_result(response)


def delete(object_url):
    """delete to object instance"""
    response = requests.delete(object_url, auth=api_auth())
    return api_result(response, as_json=False)


def put(obj_url, data):
    """update to object instance"""
    response = requests.put(obj_url, data=data, auth=api_auth())
    return api_result(response)
