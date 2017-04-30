from flask import Flask, jsonify, request, make_response

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from packages.functions import (
    __reset_db, get_collections, get_assets, get_collection_by_id,
    get_asset_by_id, get_query, post_collection, post_asset, del_asset,
    del_collection, patch_asset, get_query_flag,
    patch_collection, make_dict, get_footages, post_user, get_user, post_image, post_footage,
    to_dict, get_items, post_geometry, post_collection, get_item_by_id, patch_item_by_id, post_people
    )

from packages.models import Item

from config import cred


app = Flask(__name__)
# TODO: Global config?
#app.config.from_object('config.config')
#app.config.from_object('config')

# TODO: Auth
# TODO: api tests
# TODO: catch/process no cred file error

# config
SERVER = 'http://127.0.0.1:5050'
ROUTE = '/glance/api'

# make function for checkcing/setting db
"""
Set up dev database, if False

sudo -u postgres psql
CREATE DATABASE glance;
CREATE USER vhrender WITH PASSWORD 'vhrender2011';
ALTER ROLE vhrender SET client_encoding TO 'utf8';
ALTER ROLE vhrender SET default_transaction_isolation TO 'read committed';
ALTER ROLE vhrender SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE glance TO vhrender;
"""

engine = create_engine(
    'postgresql://{}:{}@{}:5432/glance'.format(
        cred.username, cred.password, cred.ip_local
    ), echo=False
)

# Init sessionmaker
Session = sessionmaker(bind=engine)

"""
# Dev functions
session = Session()
__reset_db(session, engine)
"""

@app.route('{}'.format(ROUTE))
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


@app.route('{}/asset'.format(ROUTE), methods=['POST', 'GET'])
def asset():
    """Endpoint that returns asset objects"""
    if request.method=='POST':
        # build query from user args
        query = {}
        for x in request.args:
            query[x] = request.args[x]

        try:
            session = Session()
            asset = post_asset(session, **query)

            result = {
                'responce': 'successful',
                'location': ROUTE + '/asset/' + str(asset.id)
            }

            session.close()

            return make_response(
                jsonify(
                    {
                        'POST: /asset': result
                    }
                )
            ), 200

        except:
            session.close()
            fail = {'Action': 'failed'}

            return make_response(
                jsonify(
                    {
                        'POST /asset': fail
                    }
                )
            ), 404

    elif request.method=='GET':
        session = Session()

        raw_assets = get_assets(session)
        assets = make_dict(raw_assets)

        if len(assets) == 0:
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
            jsonify(assets)
        ), 200

    else:
        session.close()
        return jsonify({'Asset': 'This endpoint only accepts POST, GET methods.'})


@app.route('{}/item'.format(ROUTE), methods=['POST', 'GET'])
def item():
    """Endpoint that returns asset objects"""
    if request.method=='POST':
        query = {}
        for x in request.args:
            query[x] = request.args[x]

        if query['item_type'] == 'image':
            return image()
        elif query['item_type'] == 'footage':
            return footage()
        elif query['item_type'] == 'geometry':
            return geometry()
        elif query['item_type'] == 'collection':
            return collection()
        elif query['item_type'] == 'people':
            return people()


    elif request.method=='GET':
        session = Session()

        result = get_items(session)

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

'''
@app.route('{}/collection'.format(ROUTE), methods=['POST', 'GET'])
def collection():

    if request.method=='POST':
        query = {}
        for x in request.args:
            query[x] = request.args[x]

        try:
            session = Session()
            collection = post_collection(session, **query)

            result = {
                'responce': 'successful',
                'location': ROUTE + '/collection/' + str(collection.id)
            }

            session.close()

            return make_response(
                jsonify(
                    {
                        'POST: /collection': result
                    }
                )
            ), 200

        except:
            fail = {'Action': 'failed'}
            session.close()
            return make_response(
                jsonify(
                    {
                        'POST /collection': fail
                    }
                )
            ), 404

    elif request.method=='GET':
        session = Session()
        raw_collections = get_collections(session)

        collections = make_dict(raw_collections)

        if len(collections) == 0:
            session.close()
            return make_response(
                jsonify(
                    {
                        'GET collections': {
                            'Status': 'Successful',
                            'Message': 'No collections in database'
                        }
                    }
                )
            ), 200

        session.close()
        return make_response(
            jsonify(collections)
        ), 200

    else:

        session.close()
        return jsonify({'Asset': 'This endpoint only accepts POST, GET methods.'})
'''

@app.route('{}/collection/<int:collection_id>'.format(ROUTE), methods=['GET'])
def get_collection_id(collection_id):
    # TODO : doc string
    if request.method=='GET':
        session = Session()
        raw_collection = get_collection_by_id(session, collection_id)
        collection = make_dict((raw_collection,))

    else:
        session.close()
        return jsonify({'collection': 'failed - endpoint only accepts GET methods'})

    session.close()
    return jsonify({'collection': collection})


@app.route('{}/asset/<int:asset_id>'.format(ROUTE), methods=['GET'])
def get_asset_id(asset_id):
    # TODO: Doc string
    if request.method=='GET':
        session = Session()
        raw_asset = get_asset_by_id(session, asset_id)
        asset = make_dict((raw_asset,))

    else:

        session.close()
        return jsonify({'asset': 'failed - endpoint only accepts GET methods'})

    session.close()
    return jsonify({'asset': asset})



@app.route('{}/item/<int:asset_id>'.format(ROUTE), methods=['GET'])
def get_item(asset_id):
    # TODO: Doc string
    if request.method=='GET':
        session = Session()
        raw_asset = get_item_by_id(session, asset_id)
        asset = to_dict((raw_asset,))

    else:

        session.close()
        return jsonify({'item': 'failed - endpoint only accepts GET methods'})

    session.close()
    return jsonify({'item': asset})


@app.route('{}/query'.format(ROUTE), methods=['GET'])
def query():
    """ returns results from querys
    'flag': takes key/value, returns
    'query': takes list of string, returns list of dict;
    """
    if 'flag' in request.args:
        session = Session()
        flagged = get_query_flag(session, request.args['flag'])
        session.close()

        return jsonify({'flagged assets': flagged})


    elif 'query' in request.args:
        session = Session()
        raw_assets = get_query(session, request.args)
        assets = to_dict(raw_assets)
        session.close()

        return jsonify({'result': assets})


@app.route(
    '{}/collection/delete/<int:collection_id>'.format(ROUTE), methods=['DELETE']
    )
def delete_collection(collection_id):
    # TODO: make better responce
    if request.method=='DELETE':
        session = Session()
        asset = del_collection(session, collection_id)

        if collection_id:
            result = {
                'Action': 'successful',
                'collection id': 'IMP'
            }
            session.close()
            return jsonify({'DELETE collection/delete/': result})
        else:
            result = {
                'Action': 'fail',
                'collection id': 'IMP'
            }
            session.close()
            return jsonify({'DELETE collection/delete/': result})


@app.route('{}/asset/delete/<int:asset_id>'.format(ROUTE), methods=['DELETE'])
def delete_asset(asset_id):
    # TODO: make better responce
    if request.method=='DELETE':
        session = Session()
        asset = del_asset(session, asset_id)

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


@app.route('{}/asset/patch'.format(ROUTE), methods=['PATCH'])
def patch_asset_id():
    # TODO: dont use try/except here

    patch_data = {}
    for y in request.args:
        patch_data[y] = request.args[y]

    session = Session()
    patched_asset = patch_asset(session, **patch_data)
    session.close()

    return jsonify({'PATCH': patched_asset})




@app.route('{}/item/patch'.format(ROUTE), methods=['PATCH'])
def patch_item():
    # TODO: dont use try/except here

    patch_data = {}
    for y in request.args:
        patch_data[y] = request.args[y]

    session = Session()
    patched_asset = patch_item_by_id(session, **patch_data)
    session.close()

    return jsonify({'PATCH': patched_asset})






@app.route('{}/collection/patch'.format(ROUTE), methods=['PATCH'])
def patch_collection_id():
    patch_data = {}
    for x in request.args:
        patch_data[x] = request.args.get(x)

    session = Session()
    patched_collection = patch_collection(session, **patch_data)
    session.close()

    return jsonify({'PATCH': patched_collection})


@app.route('{}/user'.format(ROUTE), methods=['POST', 'GET'])
def user():

    if request.method=='POST':
        post_data = {}

        for x in request.args:
            post_data[x] = request.args.get(x)

        session = Session()
        posted_user = post_user(session, **post_data)
        session.close()

        return jsonify({'user': 'posted_user'})

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


@app.route('{}/image'.format(ROUTE), methods=['POST', 'GET'])
def image():
    """Endpoint that returns asset objects"""
    if request.method=='POST':
        query = {}
        for x in request.args:
            query[x] = request.args[x]

        try:
            session = Session()
            asset = post_image(session, **query)

            result = {
                'responce': 'successful',
                'location': ROUTE + '/item/' + str(asset.id)
            }

            session.close()

            return make_response(
                jsonify(
                    {
                        'POST: /item': result
                    }
                )
            ), 200

        except:
            session.close()
            fail = {'Action': 'failed'}
            return make_response(
                jsonify(
                    {
                        'POST /item': fail
                    }
                )
            ), 404



    elif request.method=='GET':
        session = Session()

        result = get_items(session)

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


@app.route('{}/footage'.format(ROUTE), methods=['POST', 'GET'])
def footage():
    """Endpoint that returns asset objects"""
    if request.method=='POST':
        query = {}
        for x in request.args:
            query[x] = request.args[x]

        try:
            session = Session()
            asset = post_footage(session, **query)

            result = {
                'responce': 'successful',
                'location': ROUTE + '/item/' + str(asset.id)
            }

            session.close()

            return make_response(
                jsonify(
                    {
                        'POST: /item': result
                    }
                )
            ), 200

        except:
            session.close()
            fail = {'Action': 'failed'}
            return make_response(
                jsonify(
                    {
                        'POST /asset': fail
                    }
                )
            ), 404

    elif request.method=='GET':
        session = Session()

        result = get_items(session)

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


@app.route('{}/geometry'.format(ROUTE), methods=['POST', 'GET'])
def geometry():
    """Endpoint that returns asset objects"""
    if request.method=='POST':
        query = {}
        for x in request.args:
            query[x] = request.args[x]

        try:
            session = Session()
            asset = post_geometry(session, **query)

            result = {
                'responce': 'successful',
                'location': ROUTE + '/item/' + str(asset.id)
            }

            session.close()

            return make_response(
                jsonify(
                    {
                        'POST: /item': result
                    }
                )
            ), 200

        except:
            session.close()
            fail = {'Action': 'failed'}
            return make_response(
                jsonify(
                    {
                        'POST /item': fail
                    }
                )
            ), 404

    elif request.method=='GET':
        session = Session()

        result = get_items(session)

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


@app.route('{}/people'.format(ROUTE), methods=['POST', 'GET'])
def people():
    """Endpoint that returns asset objects"""
    if request.method=='POST':
        query = {}
        for x in request.args:
            query[x] = request.args[x]

        try:
            session = Session()
            asset = post_people(session, **query)

            result = {
                'responce': 'successful',
                'location': ROUTE + '/item/' + str(asset.id)
            }

            session.close()

            return make_response(
                jsonify(
                    {
                        'POST: /item': result
                    }
                )
            ), 200

        except:
            session.close()
            fail = {'Action': 'failed'}
            return make_response(
                jsonify(
                    {
                        'POST /item': fail
                    }
                )
            ), 404

    elif request.method=='GET':
        session = Session()

        result = get_items(session)

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



@app.route('{}/collection'.format(ROUTE), methods=['POST', 'GET'])
def collection():
    """Endpoint that returns asset objects"""
    if request.method=='POST':
        query = {}
        for x in request.args:
            query[x] = request.args[x]

        try:
            session = Session()
            asset = post_collection(session, **query)

            result = {
                'responce': 'successful',
                'location': ROUTE + '/item/' + str(asset.id)
            }

            session.close()

            return make_response(
                jsonify(
                    {
                        'POST: /item': result
                    }
                )
            ), 200

        except:
            session.close()
            fail = {'Action': 'failed'}
            return make_response(
                jsonify(
                    {
                        'POST /item': fail
                    }
                )
            ), 404

    elif request.method=='GET':
        session = Session()

        result = get_items(session)

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



if __name__ == '__main__':
    app.run(debug=True, port=5050)
