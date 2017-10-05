import requests
from requests.auth import HTTPBasicAuth

import glance.config

# TODO: Imp error handlering

# helpers
def tag_string(tag_list):
    if isinstance(tag_list, str):
        return tag_list.lower()

    elif isinstance(tag_list, list):
        return ' '.join(tag_list).lower()


def payload_from_form(requestform):
    payload = {}

    for k in requestform:
        if k == 'id':
            payload['id'] = requestform[k]

        elif k == 'append_collection' and requestform[k] != '':
            payload['items'] = requestform[k]

        elif k == 'append_to_collection' and requestform[k] != '':
            payload['append_to_collection'] = requestform[k]

        elif k == 'append_tags' and requestform[k] != '':
            payload['tags'] = requestform[k]

        elif k == 'people_tags' and requestform[k] != '':
            tags = ' '.join(requestform.getlist('people_tags'))
            payload['people_tags'] = tags

        elif k == 'collection_rename' and requestform[k] != '':
            payload[k] = requestform[k]
            if 'tags' in payload and payload['tags'] != '':
                payload['tags'] += f"{payload['tags']} {payload[k]}"
            else:
                payload['tags'] = payload[k]

        elif k == 'del_item_loc' and requestform[k] != '':
            payload['del_item_loc'] = requestform['del_item_loc']

        elif k == 'del_item_thumb' and requestform[k] != '':
            payload['del_item_thumb'] = requestform['del_item_thumb']

    return payload


# api access
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


def get_item(account_session, payload):
    res = requests.get('{}items/{}'.format(glance.config.settings.api_root, payload['id']), auth=HTTPBasicAuth(account_session['username'], account_session['password'])).json()
    if 'status' in res and res['status'] == 'success':
        return res['data']

    else:
        return res['data']


def get_items(account_session, payload=None):
    res = requests.get('{}items'.format(glance.config.settings.api_root), auth=HTTPBasicAuth(account_session['username'], account_session['password'])).json()
    if 'status' in res and res['status'] == 'success':
        return res['data']

    else:
        return res


def delete_item(account_session, payload):
    res = requests.delete('{}items/{}'.format(glance.config.settings.api_root, payload['id']), auth=HTTPBasicAuth(account_session['username'], account_session['password'])).json()
    if 'status' in res and res['status'] == 'success':
        return res

    else:
        return res


def query(account_session, payload):
    res = requests.get('{}query'.format(glance.config.settings.api_root), params=payload, auth=HTTPBasicAuth(account_session['username'], account_session['password'])).json()
    if 'status' in res and res['status'] == 'success':
        return res

    else:
        return res
