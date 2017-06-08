"""
glance api
"""

__author__ = ""
__version__ = ""
__license__ = ""

from flask import Flask, jsonify, request, make_response

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from config import settings
from packages.functions import (
    __reset_db, get_query, post_user, get_user, to_dict,
    post_collection, get_tag, get_collection_by_author, Item
    )

app = Flask(__name__)


# TODO: Auth
# TODO: api tests
# TODO: catch/process no cred file error

'''auth and config'''
'''api config'''
# TODO: Global config?
#app.config.from_object('config.config')
#app.config.from_object('config')

# development database
engine = create_engine(settings.DEV_POSTGRES_DATABASE, echo=False)

"""
# production database
engine = create_engine(settings.PROD_POSTGRES_DATABASE, echo=False)
"""
# Init sessionmaker
Session = sessionmaker(bind=engine)

'''database tools'''
"""
# Dev functions
session = Session()
__reset_db(session, engine)
"""

# info
@app.route('{}'.format(settings.ROUTE))
def api():
    """ Returns avaliable methods for the api """
    info = {
        'End Points': {
            'POST': {
                '/asset?[key]=[value]': 'Create a new asset object',
                '/collection?[key]=[value]': 'Create a new collection object'
            }, 'GET': {
                '/asset': 'Retrieve list of assets',
                '/asset/<int>': 'Retrieve single asset by ID',
                '/footage': 'Retrieve list of assets',
                '/footage/<int>': 'Retrieve single asset by ID',
                '/collection': 'Retrieve list of collections',
                '/collection/<int>': 'Retrieve single collection by ID',
                '/query?query=<str>': 'Retrieve asset/collections that match query',

            }, 'PATCH': {
                '/asset/patch?[key]=[value]': 'Update asset using key/value pairs',
                '/collection/patch?[key]=[value]': 'Update collection using key/value pairs',
            }, 'DELETE': {
                '/asset/delete/<int>': 'Remove asset via id',
                '/collection/delete/<int>': 'Remove collection via id',
            }, 'Parameters': {
                'Asset': {
                    'name': 'string', 'image': 'string', 'image_thumb': 'string',
                    'attached': 'string', 'tag': 'string',
                },
                'Collection': {
                    'name': 'string', 'image': 'string', 'image_thumb': 'string',
                    'attached': 'string', 'tag': 'string, separate with a single space only.'
                }
            }
        },
        'Maintainers': {
            'Visualhouse': 'rory.jarrel@visualhouse.co'
        }
    }
    return jsonify({'Glance WebAPI': info})


# auth
@app.route('{}/user'.format(settings.ROUTE), methods=['POST', 'GET'])
def user():

    if request.method=='POST':
        post_data = {}

        for x in request.args:
            post_data[x] = request.args.get(x)

        print(post_data)

        session = Session()
        posted_user = post_user(session, **post_data)
        session.close()

        return jsonify({'user': str(type(session))})

    elif request.method=='GET':
        user_details = {}

        username = request.args.get('username')
        password = request.args.get('password')

        session = Session()

        user_details['username'] = username
        user_details['password'] = password

        user_cred = get_user(session, **user_details)

    session.close()

    return jsonify({'user details': user_cred})


# process
@app.route('{}/item'.format(settings.ROUTE), methods=['POST', 'GET'])
def item():
    """Endpoint that returns asset objects"""
    if request.method=='POST':
        query = {}
        for x in request.args:
            query[x] = request.args[x]

        session = Session()
        test = Item(session).post(query)
        result = to_dict((test,))
        session.close()

        return make_response(
            jsonify(
                {
                    'POST: /item': result
                }
            )
        ), 200

    elif request.method=='GET':
        session = Session()

        if 'filter' in request.args:
            raw_items = Item(session).get(filter=request.args['filter'])
            result = to_dict(raw_items)
        else:
            raw_items = Item(session).get()
            result = to_dict(raw_items)

        if len(result) == 0:
            session.close()
            return make_response(
                jsonify(
                    {
                        'GET assets': {
                            'Status': 'Successful',
                            'Message': 'No assets in database'
                        }
                    }
                )
            ), 200

        session.close()
        return make_response(
            jsonify(result)
        ), 200

    else:
        session.close()
        return jsonify({'Asset': 'This endpoint only accepts POST, GET methods.'})


@app.route('{}/tag'.format(settings.ROUTE))
def tag():
    session = Session()

    data = None
    result = get_tag(session, data)
    session.close()

    return jsonify({'tags': result})


# queries
@app.route('{}/query'.format(settings.ROUTE), methods=['GET'])
def query():
    """ returns results from querys
    'flag': takes key/value, returns
    'query': takes list of string, returns list of dict;
    'filter': takes str, affects 'query';
    """
    if 'flag' in request.args:
        pass


    elif 'query' in request.args:
        print('QQQQQQQUUUUUUUUUEEEEEEERRRRRRRRRRRYYYYYY')
        # TODO: For some reason `get_query()` only accepts a dict?
        session = Session()
        raw_assets = get_query(session, request.args)
        assets = to_dict(raw_assets)

        session.close()

        return jsonify({'result': assets})


    return jsonify({'result': ''})


@app.route('{}/collection/author/<author>'.format(settings.ROUTE))
def get_collection_author(author):
    session = Session()

    raw_result = get_collection_by_author(session, author)
    result = to_dict(raw_result)

    session.close()

    return jsonify({'result': result})


@app.route('{}/item/<int:item_id>'.format(settings.ROUTE), methods=['GET'])
def get_item(item_id):
    # TODO: Doc string
    if request.method=='GET':
        session = Session()
        raw_asset = Item(session).get(item_id)
        asset = to_dict((raw_asset, ))

    else:

        session.close()
        return jsonify({'item': 'failed - endpoint only accepts GET methods'})

    session.close()
    return jsonify({'item': asset})


# crud
@app.route('{}/item/delete/<int:asset_id>'.format(settings.ROUTE), methods=['DELETE'])
def delete_asset(asset_id):
    # TODO: make better responce
    if request.method=='DELETE':
        session = Session()
        asset = Item(session).delete(asset_id)

        if asset:
            result = {
                'Action': 'successful',
                'asset id': 'IMP'
            }
            session.close()
            return jsonify({'DELETE asset/delete/': result})

        else:
            result = {
                'Action': 'fail',
                'asset id': 'IMP'
            }
            session.close()

            return jsonify({'DELETE asset/delete/': result})

    session.close()
    return jsonify({'DELETE asset/delete/': 'error?'})


@app.route('{}/item/patch'.format(settings.ROUTE), methods=['PATCH'])
def patch_item():

    # TODO: dont use try/except here

    patch_data = {}
    for y in request.args:
        patch_data[y] = request.args[y]

    session = Session()
    raw_item = Item(session).patch(patch_data)
    item = to_dict((raw_item,))
    session.close()

    return jsonify({'PATCH': item})



if __name__ == '__main__':
    app.run(debug=True, port=5050)
