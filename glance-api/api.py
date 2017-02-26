from flask import Flask, jsonify, request, make_response

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# from dev_tool import get_tables_db, get_columns_, drop_table
from models import (
    __reset_db, get_collections, get_assets, get_collection_by_id,
    get_asset_by_id, get_query, post_collection, post_asset, delete_assety,
    delete_collectiony, patch_assety, get_query_flag, get_query_tag,
    patch_collectiony
    )
from api_func import (
    connect, POST_collection, POST_asset, GET_asset, GET_collection,
    GET_collection_id, GET_asset_id, DELETE_collection, PUT_asset_tag,
    DELETE_asset, GET_query
    )
import cred


app = Flask(__name__)
# TODO: Global config?
#app.config.from_object('config.config')
#app.config.from_object('config')


# TODO: Auth
# TODO: api tests
# TODO: catch/process no cred file error


# config
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

# Make connection and Metadata object
con, meta = connect(cred.username, cred.password, 'glance', cred.ip_local)

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
                    'attached': 'string', 'tag': 'string, separate with comma (,) only.'
                },
                'Collection': {
                    'name': 'string', 'image': 'string', 'image_thumb': 'string',
                    'attached': 'string', 'tag': 'string, separate with comma (,) only.}'
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
        try:
            session = Session()
            asset = post_asset(session, **request.args)

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
        assets = get_assets(session)

        if len(assets) == 0:
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

        return make_response(
            jsonify(assets)
        ), 200

    else:
        return jsonify({'Asset': 'This endpoint only accepts POST, GET methods.'})


@app.route('{}/collection'.format(ROUTE), methods=['POST', 'GET'])
def collection():

    if request.method=='POST':

        try:
            session = Session()
            collection = post_collection(session, **request.args)

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

            return make_response(
                jsonify(
                    {
                        'POST /collection': fail
                    }
                )
            ), 404

    elif request.method=='GET':
        session = Session()
        collections = get_collections(session)

        if len(collections) == 0:
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


        return make_response(
            jsonify(collections)
        ), 200

    else:

        return jsonify({'Asset': 'This endpoint only accepts POST, GET methods.'})


@app.route('{}/collection/<int:collection_id>'.format(ROUTE), methods=['GET'])
def get_collection_id(collection_id):
    # TODO : doc string
    if request.method=='GET':
        session = Session()
        collection = get_collection_by_id(session, collection_id)

    else:

        return jsonify({'collection': 'failed - endpoint only accepts GET methods'})

    return jsonify({'collection': collection})


@app.route('{}/asset/<int:asset_id>'.format(ROUTE), methods=['GET'])
def get_asset_id(asset_id):
    # TODO: Doc string
    if request.method=='GET':
        session = Session()
        asset = get_asset_by_id(session, asset_id)

    else:

        return jsonify({'asset': 'failed - endpoint only accepts GET methods'})

    return jsonify({'asset': asset})


@app.route('{}/query'.format(ROUTE), methods=['GET'])
def query():
    # TODO: Use sessions, not con/meta
    # TODO: figure out best way to query multiple tables, with multiple search terms

    if 'flag' in request.args:
        session = Session()
        flagged = get_query_flag(session, request.args['flag'])
        session.close()

        return jsonify({'flagged assets': flagged})

    elif 'query' in request.args:
        session = Session()
        assets = get_query(session, request.args)
        session.close()

        return jsonify({'result': assets})

    elif 'tag' in request.args:

        session = Session()
        bla = get_query_tag(session)
        session.close()

        return jsonify({'result': 'tags'})

    elif 'collection' in request.args:
        return jsonify({'result': 'collections'})

    return jsonify({'result': assets})


@app.route(
    '{}/collection/delete/<int:collection_id>'.format(ROUTE), methods=['DELETE']
    )
def delete_collection(collection_id):
    # TODO: make better responce
    if request.method=='DELETE':
        session = Session()
        asset = delete_collectiony(session, collection_id)
        print('passed api model')

        if collection_id:
            result = {
                'Action': 'successful',
                'collection id': 'IMP'
            }
            return jsonify({'DELETE collection/delete/': result})
        else:
            result = {
                'Action': 'fail',
                'collection id': 'IMP'
            }

            return jsonify({'DELETE collection/delete/': result})


@app.route('{}/asset/delete/<int:asset_id>'.format(ROUTE), methods=['DELETE'])
def delete_asset(asset_id):
    # TODO: make better responce
    if request.method=='DELETE':
        session = Session()
        asset = delete_assety(session, asset_id)

        if asset:
            session.close()
            result = {
                'Action': 'successful',
                'asset id': 'IMP'
            }

            return jsonify({'DELETE asset/delete/': result})

        else:
            session.close()
            result = {
                'Action': 'fail',
                'asset id': 'IMP'
            }

            return jsonify({'DELETE asset/delete/': result})


@app.route('{}/asset/patch'.format(ROUTE), methods=['PATCH'])
def patch_asset():
    # TODO: impletement with sqlalchemy session

    patch_data = {}
    for y in request.args:
        patch_data[y] = request.args[y]

    session = Session()
    try:
        patch_assety(session, **patch_data)
    except:
        pass

    asset = get_asset_by_id(session, patch_data['id'])
    session.close()

    return jsonify({'PATCH': asset})


@app.route('{}/collection/patch'.format(ROUTE), methods=['PATCH'])
def patch_collection():
    # TODO: impletement with sqlalchemy session
    patch_data = {}
    for x in request.args:
        patch_data[x] = request.args.get(x)

    session = Session()
    try:
        patch_collectiony(session, **patch_data)
    except:
        pass

    collection = get_collection_by_id(session, patch_data['id'])
    session.close()

    return jsonify({'PATCH': collection})


if __name__ == '__main__':
    app.run(debug=True)
