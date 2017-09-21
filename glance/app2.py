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

import glance.modules.auth as auth
import glance.modules.file as file
import glance.modules.image as image

from config import settings


# TODO: collection is set to loop on 5. do this to the other pages?
# search results, front page etc.


'''Flask Config'''
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = settings.tmp_upload
app.secret_key = settings.secret_key

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

    else:
        return render_template('login.html')

    return home()


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

        r = requests.post('{}'.format(API_USER), params=payload)

        return home()

    elif request.method == 'GET':
        return render_template('signup.html')


# utility
@app.route('/append_fav', methods=['GET','POST'])
def append_fav():

    item_id = request.args['item_id']
    item_thumb = request.args['item_thumb']

    auth.SessionHandler(session).fav(item_id, item_thumb)

    return jsonify(result=len(session['fav']))


@app.route('/uploading', methods=['POST'])
def uploading():
    #TODO:  refactor.
    # TODO: user input sanitising? here or the api?
    # TODO: emi persistant data users search term, imp into session?
    data = {'query': "**"}
    if auth.logged_in(session):
        if request.method == 'POST':
            # Init dict and append user data
            upload_data = {}
            upload_data['items_for_collection'] = []
            items_for_collection = []

            for form_input in request.form:
                upload_data[form_input] = request.form[form_input]

            # process all uploaded files.
            processed_files = file.process_raw_files(request.files.getlist('file'))

            # process remaining item data
            if 'itemradio' in upload_data and upload_data['itemradio'] == 'image':
                for items in processed_files:
                    for item in processed_files[items]:
                        if item.filename.endswith('.jpg'):
                            uploaded_file = file.upload_handler(item, app.config['UPLOAD_FOLDER'])
                            payload = {}
                            payload['name'] = items
                            payload['author'] = session['username']
                            payload['tags'] = upload_data['tags']
                            payload['item_type'] = upload_data['itemradio']
                            payload['item_loc'] = uploaded_file[0]
                            payload['item_thumb'] = uploaded_file[1]

                            # AWS REKOGNITION
                            for tag in image.generate_tags(uploaded_file[0]):
                                if payload['tags'] == '':
                                    payload['tags'] = tag.lower()
                                else:
                                    payload['tags'] +=  ' ' + tag.lower()

                            # append name to tags
                            # remove punc
                            payload_name = ''
                            for x in payload['name']:
                                if x == '_' or x == '-':
                                    payload_name += ' '
                                    pass
                                elif x in string.punctuation:
                                    pass
                                else:
                                    payload_name += x
                            # apend payload_name to tag string for posting.
                            if payload['tags'] == '':
                                payload['tags'] = payload_name.lower()
                            else:
                                payload['tags'] += ' {}'.format(payload_name.lower())

                        else:
                            uploaded_file = file.upload_handler(item, app.config['UPLOAD_FOLDER'])
                            payload['attached'] = uploaded_file

                    # post payload to api
                    account_session = auth.SessionHandler(session).get()
                    r = requests.post('{}items'.format(settings.api_root), params=payload, auth=HTTPBasicAuth(account_session['username'], account_session['password']))
                    res = r.json()['data']
                    # collect uploaded item ids from respoce object in a list
                    # incase its this also a collection...
                    # TODO: above comment makes no sence... can i check if its a
                    # collection at the beginning? does it matter? Its not dry.
                    # TODO: Make this a helper
                    # res = r.json()

                    # append Item ids for Collection
                    for x in res:
                        item_id = x['id']
                        upload_data['items_for_collection'].append(item_id)

            elif 'itemradio' in upload_data and upload_data['itemradio'] == 'footage':
                # build payload for api
                for items in processed_files:
                    for item in processed_files[items]:
                        if item.filename.endswith('.mp4'):
                            uploaded_file = file.upload_handler(item, app.config['UPLOAD_FOLDER'])
                            item_thumb_filename, item_thumb_ext = os.path.splitext(uploaded_file[0])

                            payload = {}
                            payload['name'] = items
                            payload['author'] = session['username']
                            payload['tags'] = upload_data['tags']
                            payload['item_type'] = upload_data['itemradio']
                            payload['item_loc'] = uploaded_file[0]
                            payload['item_thumb'] = uploaded_file[1]

                            # AWS REKOGNITION
                            # TODO: currently running `generate_tags` on the
                            # thumbnail. Needs to be run on the extracted image.
                            for tag in image.generate_tags(uploaded_file[1]):
                                payload['tags'] +=  ' ' + tag.lower()


                        else:
                            # Use to validate wether item is a valid format
                            pass
                            """
                            uploaded_file = file.upload_handler(item, app.config['UPLOAD_FOLDER'])
                            payload['attached'] = uploaded_file
                            """

                    # append name to tags
                    # remove punc
                    payload_name = ''
                    for x in payload['name']:
                        if x == '_' or x == '-':
                            payload_name += ' '
                            pass
                        elif x in string.punctuation:
                            pass
                        else:
                            payload_name += x
                    # apend payload_name to tag string for posting.
                    if payload['tags'] == '':
                        payload['tags'] = payload_name.lower()
                    else:
                        payload['tags'] += ' {}'.format(payload_name.lower())



                    # post payload to api
                    account_session = auth.SessionHandler(session).get()
                    r = requests.post('{}items'.format(settings.api_root), params=payload, auth=HTTPBasicAuth(account_session['username'], account_session['password']))
                    res = r.json()['data']
                    payload['tags'] = ''

                    # append Item ids for Collection
                    for x in res:
                        item_id = x['id']
                        upload_data['items_for_collection'].append(item_id)

            elif 'itemradio' in upload_data and upload_data['itemradio'] == 'geometry':
                # build payload for api

                for items in processed_files:
                    # payload['name'] = items

                    for item in processed_files[items]:
                        if item.filename.endswith('.jpg'):
                            uploaded_file = file.upload_handler(item, app.config['UPLOAD_FOLDER'])

                            payload = {}
                            payload['name'] = items
                            payload['author'] = session['username']
                            payload['tags'] = upload_data['tags']
                            payload['item_type'] = upload_data['itemradio']
                            payload['item_loc'] = uploaded_file[0]
                            payload['item_thumb'] = uploaded_file[1]

                            # AWS REKOGNITION
                            for tag in image.generate_tags(uploaded_file[0]):
                                payload['tags'] +=  ' ' + tag.lower()

                        else:
                            uploaded_file = file.upload_handler(item, app.config['UPLOAD_FOLDER'])
                            payload['attached'] = uploaded_file


                    # append name to tags
                    # remove punc
                    payload_name = ''
                    for x in payload['name']:
                        if x == '_' or x == '-':
                            payload_name += ' '
                            pass
                        elif x in string.punctuation:
                            pass
                        else:
                            payload_name += x
                    # apend payload_name to tag string for posting.
                    if payload['tags'] == '':
                        payload['tags'] = payload_name.lower()
                    else:
                        payload['tags'] += ' {}'.format(payload_name.lower())



                    # post payload to api
                    account_session = auth.SessionHandler(session).get()
                    r = requests.post('{}items'.format(settings.api_root), params=payload, auth=HTTPBasicAuth(account_session['username'], account_session['password']))
                    res = r.json()['data']
                    # collect uploaded item ids from respoce object.
                    # append Item ids for Collection
                    for x in res:
                        item_id = x['id']
                        upload_data['items_for_collection'].append(item_id)

            elif 'itemradio' in upload_data and upload_data['itemradio'] == 'people':
                # build payload for api

                for items in processed_files:
                    for item in processed_files[items]:
                        if item.filename.endswith('.jpg'):
                            uploaded_file = file.upload_handler(item, app.config['UPLOAD_FOLDER'])

                            payload = {}
                            payload['name'] = items
                            payload['author'] = session['username']
                            payload['tags'] = upload_data['tags']
                            payload['item_type'] = upload_data['itemradio']
                            payload['item_loc'] = uploaded_file[0]
                            payload['item_thumb'] = uploaded_file[1]

                            # AWS REKOGNITION
                            for tag in image.generate_tags(uploaded_file[0]):
                                payload['tags'] +=  ' ' + tag.lower()

                        else:
                            uploaded_file = file.upload_handler(item, app.config['UPLOAD_FOLDER'])
                            payload['attached'] = uploaded_file


                    # append name to tags
                    # remove punc
                    payload_name = ''
                    for x in payload['name']:
                        if x == '_' or x == '-':
                            payload_name += ' '
                            pass
                        elif x in string.punctuation:
                            pass
                        else:
                            payload_name += x
                    # apend payload_name to tag string for posting.
                    if payload['tags'] == '':
                        payload['tags'] = payload_name.lower()
                    else:
                        payload['tags'] += ' {}'.format(payload_name.lower())



                    # post payload to api
                    account_session = auth.SessionHandler(session).get()
                    r = requests.post('{}items'.format(settings.api_root), params=payload, auth=HTTPBasicAuth(account_session['username'], account_session['password']))
                    res = r.json()['data']
                    # collect uploaded item ids from respoce object.
                    # TODO: Make this a helper
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

                    account_session = auth.SessionHandler(session).get()
                    r = requests.post('{}items'.format(settings.api_root), params=payload, auth=HTTPBasicAuth(account_session['username'], account_session['password']))

                    res = r.json()['data']

                    # return home()
                    return render_template('collection.html', item=res, data=data)

            elif 'collection' in upload_data:
                print('NO HIT')

                payload = {
                    'name': upload_data['collection'],
                    'item_type': 'collection',
                    'item_loc': 'site/default_cover.jpg',
                    'item_thumb': 'site/default_cover.jpg',
                    'tags': "upload_data['tags']",
                    'author': session['username']
                }

                account_session = auth.SessionHandler(session).get()
                r = requests.post('{}items'.format(settings.api_root), params=payload, auth=HTTPBasicAuth(account_session['username'], account_session['password']))
                res = r.json()['data']

                return render_template('collection.html', item=res, data=data)


            if len(upload_data['items_for_collection']) > 1:
                return render_template('uploadcomplete.html', data=data)
            elif len(upload_data['items_for_collection']) == 1:
                # TODO: return actual items. instead of 'uploadcompelte.html'.
                return render_template('uploadcomplete.html', data=data)

            else:
                return render_template('uploadcomplete.html', data=data)

    else:
        return home()


@app.route('/patch', methods=['POST'])
def patch_item():

    data = {}
    if request.method == 'POST':
        form = request.form
        for k in form:
            if k == 'id':
                data['id'] = form[k]

            elif k == 'append_collection' and form[k] != '':
                data['items'] = form[k]

            elif k == 'append_to_collection' and form[k] != '':
                data['append_to_collection'] = form[k]

            elif k == 'append_tags' and form[k] != '':
                data['tags'] = form[k]

            elif k == 'people_tags' and form[k] != '':
                tags = ' '.join(form.getlist('people_tags'))
                data['people_tags'] = tags

            elif k == 'collection_rename' and form[k] != '':
                data[k] = form[k]
                if 'tags' in data and data['tags'] != '':
                    data['tags'] += f"{data['tags']} {data[k]}"
                else:
                    data['tags'] = data[k]

        if 'change_cover' in request.files:
            cover_image = request.files['change_cover']
            if cover_image.filename == '':
                pass

            else:
                uploaded_file = file.upload_handler(cover_image, app.config['UPLOAD_FOLDER'])
                data = {}
                data['item_loc'] = uploaded_file[0]
                data['item_thumb'] = uploaded_file[1]
                data['id'] = form['id']

                data['del_item_loc'] = form['del_item_loc']
                data['del_item_thumb'] = form['del_item_thumb']

                # delete old collection cover
                if 'del_item_loc' and 'del_item_thumb' in data:
                    to_delete_from_s3 = [data['del_item_loc'], data['del_item_thumb'], 'None']
                    auth.delete_from_s3(to_delete_from_s3)

    account_session = auth.SessionHandler(session).get()
    r = requests.put('{}items/{}'.format(settings.api_root, data['id']), params=data, auth=HTTPBasicAuth(account_session['username'], account_session['password']))
    res = r.json()


    return redirect(f"item/{data['id']}")


@app.route('/manage_selection', methods=['GET', 'POST'])
def manage_selection():
    account_session = auth.SessionHandler(session).get()

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

        r = requests.put('{}items/{}'.format(settings.api_root, payload['id']), params=payload, auth=HTTPBasicAuth(account_session['username'], account_session['password']))


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

            r = requests.put('{}items/{}'.format(settings.api_root, payload['id']), params=payload, auth=HTTPBasicAuth(account_session['username'], account_session['password']))

    # TODO: IMP clearing of all selections
    if 'clear_selection' in request.form and request.form['clear_selection'] != '':
        account_session['fav'] = {}


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
            'author': account_session['username']
        }

        # r = requests.post('{}'.format(API_ITEM), params=payload)
        r = requests.post('{}items'.format(settings.api_root), params=payload, auth=HTTPBasicAuth(account_session['username'], account_session['password']))

        #clean up session object
        # account_session['fav'] = {}

        if 'status' in r.json() and r.json()['status'] == 'success':
            return item(r.json()['data'][0]['id'])


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
    reversed_list = []

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

    else:
        res = res['data']
        # tags
        tags = []
        goo = [x['tags'] for x in res]

        for x in res:
            for j in x['tags']:
                if j not in tags:
                    tags.append(j['name'])

        collections = [x for x in res if x['item_type'] == 'collection'][0:9]

        images = [x for x in res if x['item_type'] == 'image'][0:9]

        footage = [x for x in res if x['item_type'] == 'footage'][0:9]

        people = [x for x in res if x['item_type'] == 'people'][0:9]

        geometry = [x for x in res if x['item_type'] == 'geometry'][0:9]


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
    account_session = auth.SessionHandler(session).get()
    if 'username' in account_session:
        r = requests.get('{}items'.format(settings.api_root), auth=HTTPBasicAuth(account_session['username'], account_session['password']))
        res = r.json()['data']
        collections = [x for x in res if x['item_type'] == 'collection' and x['author'] == account_session['username']]

        data = ['test', 'test2']

        return render_template('manage.html', collection=collections, items=data, data=data)
    else:
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
    else:
        return home()


@app.route('/item/<id>/')
def item(id):
    # TODO: emi persistant data users search term, imp into session?
    data = {'query': "**"}

    if id:
        account_session = auth.SessionHandler(session).get()
        r = requests.get('{}items/{}'.format(settings.api_root, id), auth=HTTPBasicAuth(account_session['username'], account_session['password']))

        if r.json()['data'][0]['item_type'] == 'image':
            return render_template('image2.html', item=r.json()['data'][0], data=data)

        elif r.json()['data'][0]['item_type'] == 'collection':
            return render_template('collection.html', item=r.json()['data'], data=data)

        elif r.json()['data'][0]['item_type'] == 'footage':
            return render_template('footage2.html', item=r.json()['data'][0], data=data)

        elif r.json()['data'][0]['item_type'] == 'geometry':
            return render_template('geometry2.html', item=r.json()['data'][0], data=data)

        elif r.json()['data'][0]['item_type'] == 'people':
            tags_from_api = r.json()['data'][0]['tags']
            people_tags = image.get_people_tags(tags_from_api)

            return render_template('people2.html', item=r.json()['data'][0], people_tags=people_tags, data=data)


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


    # r = requests.get('{}query'.format(API), params=data)

    account_session = auth.SessionHandler(session).get()
    r = requests.get('{}query'.format(settings.api_root), params=data, auth=HTTPBasicAuth(account_session['username'], account_session['password']))


    return render_template('search.html', data=data, items=r.json())


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
