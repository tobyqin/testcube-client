# -*- coding: utf-8 -*-
import requests
from .request_helper import api_auth, api_result, api_url


def get(api_endpoint, params):
    """get"""
    response = requests.get(api_url(api_endpoint), params=params, auth=api_auth())
    return api_result(response)


def post(api_endpoint, data):
    """create"""
    response = requests.post(api_url(api_endpoint), data=data, auth=api_auth())
    return api_result(response)


def delete(api_endpoint, data):
    """delete"""
    response = requests.delete(api_url(api_endpoint), data=data, auth=api_auth())
    return api_result(response)


def put(api_endpoint, data):
    """update"""
    response = requests.put(api_url(api_endpoint), data=data, auth=api_auth())
    return api_result(response)
