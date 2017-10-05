"""
glance web app
"""

__author__ = ""
__version__ = "0.1"
__license__ = "./LICENSE"

import os
import subprocess
import string
import re

import requests
from flask import Flask, render_template, request, session, jsonify, url_for, redirect
from requests.auth import HTTPBasicAuth
from celery import Celery

import glance.modules.auth as auth
import glance.modules.file
import glance.modules.image as image
import glance.modules.api

from glance.config import settings


'''Flask Config'''
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = settings.tmp_upload
app.secret_key = settings.secret_key

app.config['CELERY_BROKER_URL'] = 'pyamqp://guest@localhost//'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

'''API SHORTHAND'''
# TODO: Lazy?
API = settings.api_root
API_ACCOUNTS = '{}items'.format(settings.api_root)
API_ITEM = '{}items'.format(settings.api_root)
API_PATCH = '{}items/patch'.format(settings.api_root)
API_COLLECTION = '{}collection'.format(settings.api_root)
API_USER = '{}accounts'.format(settings.api_root)
API_QUERY = '{}query'.format(settings.api_root)

'''Routes'''
# auth
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form = request.form

        if auth.SessionHandler(session).open(username=form['username'], password=form['password']):

            return home()

        else:
            auth.SessionHandler(session).close()
            message = 'Somethings wrong there. Try again.'
            return render_template('login.html', message=message)

    else:
        return render_template('login.html')


@app.route("/logout")
def logout():
    auth.SessionHandler(session).close()

    return login()


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        payload = {}
        for form_input in request.form:
            payload[form_input] = request.form[form_input]

        # TODO: below is for testing only. remove for prod
        dev_user = ['test', 'admin']
        if payload['username'] not in dev_user:
            return render_template('signup.html')
        elif payload['password'] not in dev_user:
            return render_template('signup.html')

        resp = requests.post('{}accounts'.format(settings.api_root), params=payload).json()
        if 'status' in resp and resp['status'] == 'success':
            return home()

        else:
            return render_template('signup.html', message=resp['error'])

    elif request.method == 'GET':
        return render_template('signup.html')


# utility
@app.route('/append_fav', methods=['GET', 'POST'])
def append_fav():
    item_id = request.args['item_id']
    item_thumb = request.args['item_thumb']

    auth.SessionHandler(session).fav(item_id, item_thumb)

    return jsonify(result=len(session['fav']))


@app.route('/uploading', methods=['POST'])
def uploading():
    # TODO:  refactor.
    # TODO: user input sanitising? here or the api?
    # TODO: emi persistant data users search term, imp into session?
    data = {'query': "**"}
    if auth.logged_in(session):
        if request.method == 'POST':
            # Init dict and append user data
            account_session = auth.SessionHandler(session).get()
            upload_data = {}
            upload_data['items_for_collection'] = []

            for form_input in request.form:
                upload_data[form_input] = request.form[form_input]

            # process all uploaded files.
            processed_files = glance.modules.file.process_raw_files(request.files.getlist('file'))

            # process remaining item data
            if 'itemradio' in upload_data and upload_data['itemradio'] == 'image':
                for items in processed_files:
                    uploaded_file = glance.modules.file.upload_handler(app.config['UPLOAD_FOLDER'], processed_files[items], account_session, upload_data['itemradio'])
                    if uploaded_file:
                        print('--------------------------------------')
                        print(uploaded_file)
                        for x in uploaded_file:
                            item_id = x['id']
                            upload_data['items_for_collection'].append(item_id)

            elif 'itemradio' in upload_data and upload_data['itemradio'] == 'footage':
                for items in processed_files:
                    uploaded_file = glance.modules.file.upload_handler(app.config['UPLOAD_FOLDER'], processed_files[items])
                    if uploaded_file != False:
                        payload = glance.modules.file.create_payload(account_session, upload_data, items, **uploaded_file)

                    # post payload to api
                    res = glance.modules.api.post_item(account_session, payload)
                    if res:
                        # append Item ids for Collection
                        for x in res:
                            item_id = x['id']
                            upload_data['items_for_collection'].append(item_id)

            elif 'itemradio' in upload_data and upload_data['itemradio'] == 'geometry':
                for items in processed_files:
                    uploaded_file = glance.modules.file.upload_handler(app.config['UPLOAD_FOLDER'], processed_files[items])
                    if uploaded_file != False:
                        payload = glance.modules.file.create_payload(account_session, upload_data, items, **uploaded_file)

                    # post payload to api
                    res = glance.modules.api.post_item(account_session, payload)
                    if res:
                        # append Item ids for Collection
                        for x in res:
                            item_id = x['id']
                            upload_data['items_for_collection'].append(item_id)

            elif 'itemradio' in upload_data and upload_data['itemradio'] == 'people':
                for items in processed_files:
                    uploaded_file = glance.modules.file.upload_handler(app.config['UPLOAD_FOLDER'], processed_files[items])
                    if uploaded_file != False:
                        payload = glance.modules.file.create_payload(account_session, upload_data, items, **uploaded_file)

                    # post payload to api
                    res = glance.modules.api.post_item(account_session, payload)
                    if res:
                        # append Item ids for Collection
                        for x in res:
                            item_id = x['id']
                            upload_data['items_for_collection'].append(item_id)

            # Runs if collection has been requested aswell as the uploading of files.
            if 'collection' in upload_data and 'itemradio' in upload_data:
                if upload_data['collection'] != '':

                    # add collection name to tags
                    tags_from_name = upload_data['collection'].split(' ')
                    if len(upload_data['tags']) != 0:
                        for x in tags_from_name:
                            upload_data['tags'] += ' ' + str(x)
                    else:
                        for x in tags_from_name:
                            upload_data['tags'] += ' ' + str(x)

                    payload = {
                        'name': upload_data['collection'],
                        'item_type': 'collection',
                        'item_loc': 'site/default_cover.jpg',
                        'item_thumb': 'site/default_cover.jpg',
                        'tags': upload_data['tags'],
                        'items': ' '.join(upload_data['items_for_collection']),
                        'author': session['username']
                    }

                    res = glance.modules.api.post_item(account_session, payload)

                    # return home()
                    return render_template('collection.html', item=res, data=data)

            # runs if a collection name has been entered, only.
            elif 'collection' in upload_data:
                payload = {
                    'name': upload_data['collection'],
                    'item_type': 'collection',
                    'item_loc': 'site/default_cover.jpg',
                    'item_thumb': 'site/default_cover.jpg',
                    'tags': upload_data['tags'],
                    'author': session['username']
                }

                if payload['tags'] == '':
                    del payload['tags']

                # post payload to api
                res = glance.modules.api.post_item(account_session, payload)

                return render_template('collection.html', item=res, data=data)

            # upload output
            if len(upload_data['items_for_collection']) > 1:
                data = "**"
                items = {'status': 'success', 'data': []}

                for item_id in upload_data['items_for_collection']:
                    r = requests.get('{}items/{}'.format(settings.api_root, item_id), auth=HTTPBasicAuth(account_session['username'], account_session['password'])).json()['data'][0]
                    items['data'].append(r)

                return render_template('search.html', data=data, items=items)

            elif len(upload_data['items_for_collection']) == 1:
                return redirect(f"item/{upload_data['items_for_collection'][0]}")

            else:
                return render_template('uploadcomplete.html')

    else:
        return home()


@app.route('/patch', methods=['POST'])
def patch_item():
    account_session = auth.SessionHandler(session).get()
    payload = {}

    if request.method == 'POST':
        form = request.form
        for k in form:
            if k == 'id':
                payload['id'] = form[k]

            elif k == 'append_collection' and form[k] != '':
                payload['items'] = form[k]

            elif k == 'append_to_collection' and form[k] != '':
                payload['append_to_collection'] = form[k]

            elif k == 'append_tags' and form[k] != '':
                payload['tags'] = form[k]

            elif k == 'people_tags' and form[k] != '':
                tags = ' '.join(form.getlist('people_tags'))
                payload['people_tags'] = tags

            elif k == 'collection_rename' and form[k] != '':
                payload[k] = form[k]
                if 'tags' in payload and payload['tags'] != '':
                    payload['tags'] += f"{payload['tags']} {payload[k]}"
                else:
                    payload['tags'] = payload[k]

        if 'change_cover' in request.files:
            cover_image = request.files['change_cover']
            if cover_image.filename == '':
                pass

            else:
                uploaded_file = glance.modules.file.upload_handler(app.config['UPLOAD_FOLDER'], cover_image, account_session, None)
                if payload:
                    pass
                else:
                    payload = {}

                payload['item_loc'] = uploaded_file[0]
                payload['item_thumb'] = uploaded_file[1]
                payload['id'] = form['id']

                payload['del_item_loc'] = form['del_item_loc']
                payload['del_item_thumb'] = form['del_item_thumb']

                # delete old collection cover
                if 'del_item_loc' and 'del_item_thumb' in payload:
                    to_delete_from_s3 = [payload['del_item_loc'], payload['del_item_thumb'], 'None']
                    auth.delete_from_s3(to_delete_from_s3)

    glance.modules.api.put_item(account_session, payload)

    return redirect(f"item/{payload['id']}")


@app.route('/manage_selection', methods=['GET', 'POST'])
def manage_selection():
    account_session = auth.SessionHandler(session)

    if 'collection_append' in request.form and request.form['collection_append'] != '':
        payload = {}
        payload['id'] = request.form['collection_append']

        # get items in selection
        ids = []
        form_dict = request.form.to_dict()
        for x in form_dict:
            if form_dict[x] == 'on':
                ids.append(x)

        payload['items'] = ' '.join(ids)

        r = requests.put('{}items/{}'.format(settings.api_root, payload['id']), params=payload, auth=HTTPBasicAuth(account_session.get()['username'], account_session.get()['password']))


    if 'tags' in request.form and request.form['tags'] != '':
        # imp appending all tags to each item in selection

        #get selection
        # get items in selection
        ids = []
        form_dict = request.form.to_dict()
        for x in form_dict:
            if form_dict[x] == 'on':
                ids.append(x)

        # get tags

        payload = {}

        for x in ids:
            payload['id'] = x
            payload['tags'] = request.form['tags']

            r = requests.put('{}items/{}'.format(settings.api_root, payload['id']), params=payload, auth=HTTPBasicAuth(account_session.get()['username'], account_session.get()['password']))

    # TODO: IMP clearing of all selections
    if 'clear_selection' in request.form and request.form['clear_selection'] == 'True':
        args = request.form.to_dict()

        items_to_remove_from_selection = []
        for k in args:
            if args[k] == 'on':
                items_to_remove_from_selection.append(k)

        for item in items_to_remove_from_selection:
            if item in account_session.get()['fav']:
                account_session.fav(item)

        return manage()


    if 'collection_name' in request.form and request.form['collection_name'] != '':
        # IMP using checked == 'on'
        if 'fav' in session:
            items = []
            for x in session['fav']:
                items.append(x)

        payload = {
            'name': request.form['collection_name'],
            'item_type': 'collection',
            'item_loc': 'site/default_cover.jpg',
            'item_thumb': 'site/default_cover.jpg',
            'tags': request.form['collection_name'].split(' '),
            'items': ' '.join(items),
            'author': account_session.get()['username']
        }


        # r = requests.post('{}'.format(API_ITEM), params=payload)
        r = requests.post('{}items'.format(settings.api_root), params=payload, auth=HTTPBasicAuth(account_session.get()['username'], account_session.get()['password']))

        if 'status' in r.json() and r.json()['status'] == 'success':
            return item(r.json()['data'][0]['id'])


    if 'delete_selection' in request.form and request.form['delete_selection'] == 'True':
        args = request.form.to_dict()

        items_for_deletion = []
        for k in args:
            if args[k] == 'on':
                items_for_deletion.append(k)

        for item in items_for_deletion:
            g = requests.get('{}items/{}'.format(settings.api_root, item), auth=HTTPBasicAuth(account_session.get()['username'], account_session.get()['password'])).json()

            if 'status' in g and g['status'] == 'success':
                resp = g['data'][0]
                data = []
                if 'item_loc' in resp:
                    data.append(resp['item_loc'])
                if 'item_thumb' in resp:
                    data.append(resp['item_thumb'])
                if 'attached' in resp:
                    data.append(resp['attached'])

                # delete from s3 and database
                # TODO: IMP something safer.
                if item in account_session.get()['fav']:
                    account_session.fav(item)

                auth.delete_from_s3(data)
                requests.delete('{}items/{}'.format(settings.api_root, item), auth=HTTPBasicAuth(account_session.get()['username'], account_session.get()['password']))


        return manage()


    return home()


@app.route('/item/delete/<int:id>')
def delete(id):
    account_session = auth.SessionHandler(session).get()
    g = requests.get('{}items/{}'.format(settings.api_root, id), auth=HTTPBasicAuth(account_session['username'], account_session['password']))

    resp = g.json()['data'][0]
    data = []
    if 'item_loc' in resp:
        data.append(resp['item_loc'])
    if 'item_thumb' in resp:
        data.append(resp['item_thumb'])
    if 'attached' in resp:
        data.append(resp['attached'])

    # delete from s3 and database
    # TODO: IMP something safer.
    auth.delete_from_s3(data)
    requests.delete('{}items/{}'.format(settings.api_root, id), auth=HTTPBasicAuth(account_session['username'], account_session['password']))


    return home()


# display
@app.route('/')
def home():
    """Serves front page
    :return: dict. Each item tyoe.
    """

    # TODO: emi persistant data users search term, imp into session?
    data = {'query': "**"}
    # process and reverse data so the latest uploaded items are first.
    # Currently using the items `id`, but upload date would be better.

    payload = {}
    payload['filter'] = 'all'
    auth.SessionHandler(session).filter(payload['filter'])

    account_session = auth.SessionHandler(session).get()
    if 'username' not in account_session:
        return redirect(url_for('login'))

    r = requests.get('{}items'.format(settings.api_root), auth=HTTPBasicAuth(account_session['username'], account_session['password']))
    res = r.json()

    if 'status' in res and res['status'] == 'failed':
        return render_template('home.html', data=data)

    res = res['data']
    # tags
    tags = []

    for x in res:
        for j in x['tags']:
            if j not in tags:
                tags.append(j['name'])

    collections = [x for x in res if x['item_type'] == 'collection'][0:10]

    images = [x for x in res if x['item_type'] == 'image'][0:10]

    footage = [x for x in res if x['item_type'] == 'footage'][0:10]

    people = [x for x in res if x['item_type'] == 'people'][0:10]

    geometry = [x for x in res if x['item_type'] == 'geometry'][0:10]


    return render_template(
        'home.html', collections=collections, images=images, footage=footage,
        people=people, geometry=geometry, data=data, tags=tags[:160]
        )


@app.route('/manage')
def manage():
    # TODO: emi persistant data users search term, imp into session?
    data = {'query': "**"}
    # TODO: API needs to be able to serve, `item by author`.
    # data to send... collections made by user
    # TODO: data=data somethings up here.
    account_session = auth.SessionHandler(session).get()
    if 'username' in account_session:
        r = requests.get('{}items'.format(settings.api_root), auth=HTTPBasicAuth(account_session['username'], account_session['password']))
        res = r.json()
        if 'status' in res and res['status'] == 'success':
            res = r.json()['data']
            collections = [x for x in res if x['item_type'] == 'collection' and x['author'] == account_session['username']]
            data = []

            return render_template('manage.html', collection=collections, items=data, data=data)


        collections = []
        data = []
        return render_template('manage.html', collection=collections, items=data, data=data)

    return home()


@app.route('/coll_list')
def coll_list():
    data = []

    account_session = auth.SessionHandler(session).get()
    r = requests.get('{}query'.format(settings.api_root), params=data, auth=HTTPBasicAuth(account_session['username'], account_session['password']))
    collection = r.json()


    return render_template('coll_list.html', data=data, collection=collection)


@app.route('/upload')
def upload():
    # TODO: emi persistant data users search term, imp into session?
    data = {'query': "**"}

    if auth.logged_in(session):
        return render_template('upload.html', data=data)

    return home()


@app.route('/item/<id>/')
def item(id):
    data = {'query': "**"}

    if id:
        account_session = auth.SessionHandler(session).get()
        r = requests.get('{}items/{}'.format(settings.api_root, id), auth=HTTPBasicAuth(account_session['username'], account_session['password']))

        if r.json()['data'][0]['item_type'] == 'image':
            return render_template('image.html', item=r.json()['data'][0], data=data)

        elif r.json()['data'][0]['item_type'] == 'collection':
            return render_template('collection.html', item=r.json()['data'], data=data)

        elif r.json()['data'][0]['item_type'] == 'footage':
            return render_template('footage.html', item=r.json()['data'][0], data=data)

        elif r.json()['data'][0]['item_type'] == 'geometry':
            return render_template('geometry.html', item=r.json()['data'][0], data=data)

        elif r.json()['data'][0]['item_type'] == 'people':
            tags_from_api = r.json()['data'][0]['tags']
            people_tags = image.get_people_tags(tags_from_api)

            return render_template('people.html', item=r.json()['data'][0], people_tags=people_tags, data=data)


        else:
            return home()
    else:
        return home()


@app.route('/search')
def search():
    # collection init data
    data = {
        'filter': session['filter'],
        'filter_people': [],
        'query': request.args['search']
    }

    # if sent with 'filter'
    if 'filter' in request.args:
        # update data user session
        auth.SessionHandler(session).filter(request.args['filter'])
        data['filter'] = request.args['filter']
    elif 'filter_people' in request.args:
        # update user session
        auth.SessionHandler(session).filter_people(request.args['filter_people'])
    else:
        data['filter'] = session['filter']

    # get`people_filters`
    if data['filter'] == 'people':
        # collect all True 'filter_people' tags, append to query
        if 'filter_people' in session:
            for subject in session['filter_people']:
                for tag in session['filter_people'][subject]:
                    if session['filter_people'][subject][tag] == 1:
                        data['filter_people'].append(tag)
        else:
            session['filter_people'] = {}


    data['filter_people'] = ' '.join(data['filter_people'])

    account_session = auth.SessionHandler(session).get()
    r = requests.get('{}query'.format(settings.api_root), params=data, auth=HTTPBasicAuth(account_session['username'], account_session['password']))

    print('0000000000000000000000000000000000000')
    print(r.json())
    return render_template('search.html', data=data, items=r.json())


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
