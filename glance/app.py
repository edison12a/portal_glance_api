import os
import requests

from flask import Flask, flash, redirect, render_template, request, session, abort

from packages.function import LoggedIn, CheckLoginDetails, upload_handler, process_raw_files, item_to_session


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


@app.route('/')
def home():
    if LoggedIn(session):

        # process and reverse data so the latest uploaded items are first.
        # Currently using the items `id`, but upload date would be better.
        reversed_list = []
        r = requests.get('{}'.format(API_ASSET))
        for x in r.json():
            reversed_list.append(x)
        data = reversed_list[::-1]

        return render_template('home.html', items=data)
    else:
        return render_template('index.html')


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


@app.route('/upload')
def upload():
    if LoggedIn(session):
        return render_template('upload.html')
    else:
        return home()


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

                        else:
                            uploaded_file = upload_handler(item, app.config['UPLOAD_FOLDER'])
                            payload['attached'] = uploaded_file

                    # post payload to api
                    r = requests.post('{}'.format(API_ITEM), params=payload)
                    # collect uploaded item ids from respoce object.
                    res = r.json()
                    for x in res:
                        item_id = res[x]['location'].split('/')[-1]
                        upload_data['items_for_collection'].append(item_id)


            elif upload_data['itemradio'] == 'footage':
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
                    r = requests.post('{}'.format(API_ITEM), params=payload)
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

                        else:
                            uploaded_file = upload_handler(item, app.config['UPLOAD_FOLDER'])
                            payload['attached'] = uploaded_file

                    # post payload to api
                    r = requests.post('{}'.format(API_ITEM), params=payload)
                    # collect uploaded item ids from respoce object.
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
                        'items': ' '.join(upload_data['items_for_collection'])
                    }

                    print(payload)

                    r = requests.post('{}'.format(API_ITEM), params=payload)

            return render_template('uploadcomplete.html')
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

    else:
        return home()


@app.route('/search')
def search():
    search_data = {}
    search_term = request.args['search']
    search_data['query'] = str(search_term)

    r = requests.get('{}/query'.format(API), params=search_data)

    return render_template('search.html', data=search_data, items=r.json()['result'])


@app.route('/patch', methods=['POST'])
def patch_item():

    data = {}
    if request.method == 'POST':
        form = request.form
        for k in form:
            if k == 'append_collection':
                data['items'] = form[k]
            else:
                data[k] = form[k]

    r = requests.patch('{}/patch'.format(API_ITEM), params=data)
    g = requests.get('{}/item/{}'.format(API, data['id']))

    return render_template('item.html', item=g.json())

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
