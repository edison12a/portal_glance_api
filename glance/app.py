"""
glance webapp
"""

__author__ = ""
__version__ = "0.1"
__license__ = "./LICENSE"

from flask import Flask, render_template, request, session, jsonify, redirect
from celery import Celery

import glance.modules.auth as auth
import glance.modules.file
import glance.modules.image
import glance.modules.api
import glance.config


'''Flask Config'''
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = glance.config.settings.tmp_upload
app.secret_key = glance.config.settings.secret_key

app.config['CELERY_BROKER_URL'] = 'pyamqp://guest@localhost//'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

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

        res = glance.modules.api.post_account(payload)
        if res['status'] == 'success':
            return home()

        else:
            return render_template('signup.html', message=res['error'])

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

            # process form data
            for form_input in request.form:
                upload_data[form_input] = request.form[form_input]

            # process all uploaded files.
            processed_files = glance.modules.file.process_raw_files(request.files.getlist('file'))

            # process remaining item data
            if 'itemradio' in upload_data:
                for items in processed_files:
                    uploaded_file = glance.modules.file.upload_handler(app.config['UPLOAD_FOLDER'], processed_files[items], account_session, upload_data)
                    if uploaded_file:
                        # add new id to list
                        for x in uploaded_file:
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
                    payload = {'id': item_id}
                    res = glance.modules.api.get_item(account_session, payload)[0]
                    
                    items['data'].append(res)

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
        payload = glance.modules.api.payload_from_form(request.form)

        if 'change_cover' in request.files:
            cover_image = request.files['change_cover']
            if cover_image.filename == '':
                pass

            else:
                uploaded_file = glance.modules.file.upload_handler(app.config['UPLOAD_FOLDER'], cover_image, account_session, None)
                
                payload['item_loc'] = uploaded_file[0]
                payload['item_thumb'] = uploaded_file[1]

                # delete old collection cover
                if 'del_item_loc' and 'del_item_thumb' in payload:
                    auth.delete_from_s3([payload['del_item_loc'], payload['del_item_thumb'], 'None'])

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

        glance.modules.api.put_item(account_session.get(), payload)

        return redirect(f"item/{payload['id']}")


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
            payload['tags'] = glance.modules.api.tag_string(request.form['tags'])

            glance.modules.api.put_item(account_session.get(), payload)

        return manage()


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

        res = glance.modules.api.post_item(account_session.get(), payload)
        if res:
            return redirect(f"item/{res[0]['id']}")


    if 'delete_selection' in request.form and request.form['delete_selection'] == 'True':
        args = request.form.to_dict()

        items_for_deletion = []
        for k in args:
            if args[k] == 'on':
                items_for_deletion.append(k)

        for item in items_for_deletion:
            payload = {'id': item}
            resp = glance.modules.api.get_item(account_session.get(), payload)[0]
            
            data = []
            if 'item_loc' in resp:
                data.append(resp['item_loc'])
            if 'item_thumb' in resp:
                data.append(resp['item_thumb'])
            if 'attached' in resp:
                data.append(resp['attached'])

            # delete from s3 and database
            # TODO: IMP something safer.
            # upon deletion remove item from favs
            if item in account_session.get()['fav']:
                account_session.fav(item)

            auth.delete_from_s3(data)
            glance.modules.api.delete_item(account_session.get(), payload)


        return manage()


    return home()


@app.route('/item/delete/<int:id>')
def delete(id):
    account_session = auth.SessionHandler(session)
    payload = {'id': id}

    resp = glance.modules.api.get_item(account_session.get(), payload)[0]

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
    glance.modules.api.delete_item(account_session.get(), payload)

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

    account_session = auth.SessionHandler(session)
    if 'username' not in account_session.get():
        return login()

    res = glance.modules.api.get_items(account_session.get())

    total_items = glance.modules.api.total_items(account_session.get())

    if 'status' in res and res['status'] == 'success':
        tags = []

        for x in res['data']:
            for j in x['tags']:
                if j not in tags:
                    tags.append(j['name'])

        collections = [x for x in res['data'] if x['item_type'] == 'collection'][-10:]
        images = [x for x in res['data'] if x['item_type'] == 'image'][-10:]
        footage = [x for x in res['data'] if x['item_type'] == 'footage'][-10:]
        people = [x for x in res['data'] if x['item_type'] == 'people'][-10:]
        geometry = [x for x in res['data'] if x['item_type'] == 'geometry'][-10:]

        return render_template(
            'home.html', collections=collections, images=images, footage=footage,
            people=people, geometry=geometry, data=data, tags=tags[-160:], total_items=total_items
            )

    else:
        return render_template('home.html', data=data)


@app.route('/manage')
def manage():
    account_session = auth.SessionHandler(session).get()
    data = {'query': "**"}

    if 'username' in account_session:
        res = glance.modules.api.get_items(account_session)
        if res:
            collections = [x for x in res['data'] if x['item_type'] == 'collection' and x['author'] == account_session['username']]
            data = []

            return render_template('manage.html', collection=collections, items=data, data=data)

        else:
            collections = []
            data = []

            return render_template('manage.html', collection=collections, items=data, data=data)

    return home()


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
        account_session = auth.SessionHandler(session)
        payload = {'id': id}
        res = glance.modules.api.get_item(account_session.get(), payload)

        if res:
            if res[0]['item_type'] == 'image':
                return render_template('image.html', item=res[0], data=data)

            elif res[0]['item_type'] == 'collection':
                return render_template('collection.html', item=res, data=data)

            elif res[0]['item_type'] == 'footage':
                return render_template('footage.html', item=res[0], data=data)

            elif res[0]['item_type'] == 'geometry':
                return render_template('geometry.html', item=res[0], data=data)

            elif res[0]['item_type'] == 'people':
                tags_from_api = res[0]['tags']
                people_tags = glance.modules.image.get_people_tags(tags_from_api)

                return render_template('people.html', item=res[0], people_tags=people_tags, data=data)

        else:
            return home()
    else:
        return home()


@app.route('/search')
def search():
    account_session = auth.SessionHandler(session)
    data = {
        'filter': session['filter'],
        'filter_people': [],
        'query': request.args['query']
    }

    # if sent with 'filter'
    if 'filter' in request.args:
        # update data user session
        account_session.filter(request.args['filter'])
        data['filter'] = request.args['filter']
    elif 'filter_people' in request.args:
        # update user session
        account_session.filter_people(request.args['filter_people'])
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

    res = glance.modules.api.query(account_session.get(), data)

    if res:
        return render_template('search.html', data=data, items=res)
    
    else:
        return render_template('search.html', data=data, items=res)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
