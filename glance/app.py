import os
import subprocess
import random

import requests
from flask import Flask, flash, redirect, render_template, request, session, abort, jsonify

from packages.function import LoggedIn, CheckLoginDetails, upload_handler, process_raw_files, item_to_session, rektest

'''config'''
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/tmp')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# TODO: make a dev and production config, dont use secret_key in prob.
app.secret_key = os.urandom(12)

API = 'http://127.0.0.1:5050/glance/api'
API_ASSET = 'http://127.0.0.1:5050/glance/api/item'
API_ITEM = 'http://127.0.0.1:5050/glance/api/item'
API_IMAGE = 'http://127.0.0.1:5050/glance/api/image'
API_FOOTAGE = 'http://127.0.0.1:5050/glance/api/footage'
API_GEOMETRY = 'http://127.0.0.1:5050/glance/api/geometry'
API_COLLECTION = 'http://127.0.0.1:5050/glance/api/collection'
API_TAG = 'http://127.0.0.1:5050/glance/api/tag'

'''routes'''
# auth
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        form = request.form

        data = {
            'username': form['username'],
            'password': form['password']
        }

        if CheckLoginDetails(**data):
            session['logged_in'] = True
            session['user'] = data['username']
        else:
            # TODO: Something here?
            pass

    return home()


@app.route("/logout")
def logout():
    session['logged_in'] = False

    return home()


# utility
@app.route('/append_fav', methods=['GET','POST'])
def append_fav():

    item_id = request.args['item_id']
    item_thumb = request.args['item_thumb']

    if 'fav' in session:
        session['fav'].append({item_id: item_thumb})
        session.modified = True
    elif 'fav' not in session:
        session['fav'] = []
        session['fav'].append({item_id: item_thumb})
        session.modified = True

    return jsonify(result=len(session['fav']))


@app.route('/uploading', methods=['POST'])
def uploading():
    if LoggedIn(session):
        if request.method == 'POST':
            # Init dict and append user data
            upload_data = {}
            upload_data['items_for_collection'] = []
            items_for_collection = []

            for form_input in request.form:
                upload_data[form_input] = request.form[form_input]

            # process all uploaded files.
            processed_files = process_raw_files(request.files.getlist('file'))

            # Gather generic item data
            payload = {}
            payload['author'] = session['user']
            payload['tags'] = upload_data['tags']
            payload['item_type'] = upload_data['itemradio']

            # process remaining item data
            if upload_data['itemradio'] == 'image':
                for items in processed_files:
                    payload['name'] = items

                    for item in processed_files[items]:
                        if item.filename.endswith('.jpg'):
                            uploaded_file = upload_handler(item, app.config['UPLOAD_FOLDER'])
                            payload['item_loc'] = uploaded_file
                            payload['item_thumb'] = uploaded_file

                            # AWS REKOGNITION
                            for tag in rektest(uploaded_file):
                                payload['tags'] += tag.lower() + ' '

                        else:
                            uploaded_file = upload_handler(item, app.config['UPLOAD_FOLDER'])
                            payload['attached'] = uploaded_file

                    # post payload to api
                    r = requests.post('{}'.format(API_ITEM), params=payload)
                    payload['tags'] = ''
                    # collect uploaded item ids from respoce object.
                    # TODO: Make this a helper
                    res = r.json()
                    for x in res:
                        item_id = res[x]['location'].split('/')[-1]
                        upload_data['items_for_collection'].append(item_id)

            elif upload_data['itemradio'] == 'footage':
                # TODO: IMP Uploading mp4s to footage, and extracting first
                # frame as the `item_`

                # build payload for api
                for items in processed_files:
                    payload['name'] = items

                    for item in processed_files[items]:
                        if item.filename.endswith('.mp4'):
                            uploaded_file = upload_handler(item, app.config['UPLOAD_FOLDER'])
                            item_thumb_filename, item_thumb_ext = os.path.splitext(uploaded_file)

                            payload['item_loc'] = uploaded_file
                            payload['item_thumb'] = '{}.jpg'.format(item_thumb_filename)

                            # AWS REKOGNITION
                            for tag in rektest('{}.jpg'.format(item_thumb_filename)):
                                payload['tags'] += tag.lower() + ' '

                        else:
                            # Use to validate wether item is a valid format
                            pass
                            """
                            uploaded_file = upload_handler(item, app.config['UPLOAD_FOLDER'])
                            payload['attached'] = uploaded_file
                            """

                    # post payload to api
                    r = requests.post('{}'.format(API_ITEM), params=payload)
                    payload['tags'] = ''
                    # collect uploaded item ids from respoce object.
                    res = r.json()
                    for x in res:
                        item_id = res[x]['location'].split('/')[-1]
                        upload_data['items_for_collection'].append(item_id)

            elif upload_data['itemradio'] == 'geometry':
                # build payload for api

                for items in processed_files:
                    payload['name'] = items

                    for item in processed_files[items]:
                        if item.filename.endswith('.jpg'):
                            uploaded_file = upload_handler(item, app.config['UPLOAD_FOLDER'])
                            payload['item_loc'] = uploaded_file
                            payload['item_thumb'] = uploaded_file

                            # AWS REKOGNITION
                            for tag in rektest(uploaded_file):
                                payload['tags'] += tag.lower() + ' '

                        else:
                            uploaded_file = upload_handler(item, app.config['UPLOAD_FOLDER'])
                            payload['attached'] = uploaded_file

                    # post payload to api
                    r = requests.post('{}'.format(API_ITEM), params=payload)
                    # collect uploaded item ids from respoce object.
                    payload['tags'] = ''
                    res = r.json()
                    for x in res:
                        item_id = res[x]['location'].split('/')[-1]
                        upload_data['items_for_collection'].append(item_id)


            elif upload_data['itemradio'] == 'people':
                # build payload for api

                for items in processed_files:
                    payload['name'] = items

                    for item in processed_files[items]:
                        if item.filename.endswith('.jpg'):
                            uploaded_file = upload_handler(item, app.config['UPLOAD_FOLDER'])
                            payload['item_loc'] = uploaded_file
                            payload['item_thumb'] = uploaded_file

                            # AWS REKOGNITION
                            for tag in rektest(uploaded_file):
                                payload['tags'] += tag.lower() + ' '

                        else:
                            uploaded_file = upload_handler(item, app.config['UPLOAD_FOLDER'])
                            payload['attached'] = uploaded_file

                    # post payload to api
                    r = requests.post('{}'.format(API_ITEM), params=payload)
                    payload['tags'] = ''
                    # collect uploaded item ids from respoce object.
                    # TODO: Make this a helper
                    res = r.json()
                    for x in res:
                        item_id = res[x]['location'].split('/')[-1]
                        upload_data['items_for_collection'].append(item_id)


            elif upload_data['itemradio'] == 'collection':
                # build payload for api

                for items in processed_files:
                    payload['name'] = items

                    for item in processed_files[items]:
                        if item.filename.endswith('.jpg'):
                            uploaded_file = upload_handler(item, app.config['UPLOAD_FOLDER'])
                            payload['item_loc'] = uploaded_file
                            payload['item_thumb'] = uploaded_file

                        else:
                            uploaded_file = upload_handler(item, app.config['UPLOAD_FOLDER'])
                            payload['attached'] = uploaded_file

                    # post payload to api
                    r = requests.post('{}'.format(API_COLLECTION), params=payload)

            # Runs if collection has been requested aswell as the uploading of files.
            if 'collection' in upload_data:
                if upload_data['collection'] != '':
                    payload = {
                        'name': upload_data['collection'],
                        'item_type': 'collection',
                        'item_loc': 'site/default_cover.jpg',
                        'item_thumb': 'site/default_cover.jpg',
                        'tags': upload_data['tags'],
                        'items': ' '.join(upload_data['items_for_collection']),
                        'author': session['user']
                    }

                    r = requests.post('{}'.format(API_ITEM), params=payload)

                    res = r.json()
                    for x in res:
                        item_id = res[x]['location'].split('/')[-1]
                        bla = requests.get('{}/{}'.format(API_ITEM, item_id))

                        return render_template('collection.html', item=bla.json()['item'])

                return home()

            return render_template('uploadcomplete.html')
    else:
        return home()


@app.route('/patch', methods=['POST'])
def patch_item():

    data = {}
    if request.method == 'POST':
        form = request.form
        for k in form:
            if k == 'append_collection':
                data['items'] = form[k]

            elif k == 'append_tags':
                data['tags'] = form[k]

            else:
                data[k] = form[k]

    r = requests.patch('{}/patch'.format(API_ITEM), params=data)

    responce = r.json()['PATCH']
    for x in responce:
        if 'id' in x:
            return item(x['id'])

    return home()


# display
@app.route('/newcollection', methods=['GET', 'POST'])
def newcollection():

    bla = requests.get('{}/{}'.format(API_ITEM, 15))

    return render_template('collection.html', item=bla.json())


@app.route('/')
def home():
    if LoggedIn(session):

        # process and reverse data so the latest uploaded items are first.
        # Currently using the items `id`, but upload date would be better.
        reversed_list = []

        payload = {}
        if 'filter' in request.args:
            payload['filter'] = request.args['filter']

        r = requests.get('{}'.format(API_ITEM), params=payload)
        for x in r.json():
            reversed_list.append(x)
        data = reversed_list[::-1]

        # Tag data
        tags = [x for x in requests.get('{}'.format(API_TAG)).json()['tags'] if x != '']

        return render_template('home.html', items=data, tags=tags)
    else:
        return render_template('index.html')


@app.route('/favorite')
def favorite():
    # TODO: On fav click, redirect to current page, without re-loading page?
    # Maybe look into AJAX?
    # TODO: API needs to be able to serve, `item by author`.
    if LoggedIn(session):
        # data to send... collections made by user

        data = ['test', 'test2']

        return render_template('favorite.html', items=data)
    else:
        return home()


@app.route('/upload')
def upload():
    if LoggedIn(session):
        return render_template('upload.html')
    else:
        return home()


@app.route('/item/<id>/')
def item(id):

    r = requests.get('{}/{}'.format(API_ITEM, id))

    if r.json()['item'][0]['item_type'] == 'image':
        return render_template('image.html', item=r.json()['item'])

    elif r.json()['item'][0]['item_type'] == 'collection':
        return render_template('collection.html', item=r.json()['item'])

    elif r.json()['item'][0]['item_type'] == 'footage':
        return render_template('footage.html', item=r.json()['item'])

    elif r.json()['item'][0]['item_type'] == 'geometry':
        return render_template('geometry.html', item=r.json()['item'])

    elif r.json()['item'][0]['item_type'] == 'people':
        return render_template('people.html', item=r.json()['item'])


    else:
        return home()


@app.route('/search')
def search():
    search_data = {}
    search_term = request.args['search']
    search_data['query'] = str(search_term)

    if 'filter' in request.args:
        search_data['filter'] = request.args['filter']
    else:
        search_data['filter'] = 'all'

    r = requests.get('{}/query'.format(API), params=search_data)

    return render_template('search.html', data=search_data, items=r.json()['result'])


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
