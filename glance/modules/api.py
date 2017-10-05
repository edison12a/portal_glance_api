import requests
from requests.auth import HTTPBasicAuth

import glance.config


'''API SHORTHAND'''
# TODO: Lazy?
API = glance.config.settings.api_root
API_ACCOUNTS = '{}items'.format(API)
API_ITEM = '{}items'.format(API)
API_PATCH = '{}items/patch'.format(API)
API_COLLECTION = '{}collection'.format(API)
API_USER = '{}accounts'.format(API)
API_QUERY = '{}query'.format(API)

def post_item(account_session, payload):
    res = requests.post('{}items'.format(glance.config.settings.api_root), params=payload, auth=HTTPBasicAuth(account_session['username'], account_session['password'])).json()
    if 'status' in res and res['status'] == 'success':
        return res['data']

    else:
        return False


def put_item(account_session, payload):
    res = requests.put('{}items/{}'.format(glance.config.settings.api_root, payload['id']), params=payload, auth=HTTPBasicAuth(account_session['username'], account_session['password'])).json()
    if 'status' in res and res['status'] == 'success':
        return res['data']

    else:
        return False


def post_account(payload):
    res = requests.post('{}accounts'.format(glance.config.settings.api_root), params=payload).json()
    if 'status' in res and res['status'] == 'success':
        return res['data']
    
    else:
        return res['data']