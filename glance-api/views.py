from flask import Flask, jsonify, request, make_response

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# from dev_tool import get_tables_db, get_columns_, drop_table
from models import (
    reset_db, get_collections, get_assets, get_collection_by_id,
    get_asset_by_id
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

# TODO: refactor - post, get, put, delete can be used all on the same URI
# TODO: research - Should connect() be getting closed at some onepoint? Is it?
# TODO: Auth
# TODO: api tests
# TODO: Make_response, and http codes
# TODO: catch/process no cred file error



# config
ROUTE = '/glance/api'

# function for checkcing/setting db
"""
Set up dev database, if False

sudo -u postgres psql
CREATE DATABASE glance;
CREATE USER vhrender WITH PASSWORD 'vhrender2011';
ALTER ROLE vhrender SET client_encoding TO 'utf8';
ALTER ROLE vhrender SET default_transaction_isolation TO 'read committed';
ALTER ROLE vhrender SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE issues TO vhrender;
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
reset_db(session, engine)
"""

@app.route('{}'.format(ROUTE))
def api():
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
    """Endpoint that returns asset objects
        POST: AUG: name, image, tag, author, image_thumb, attached
            Returns: Responce, location
        GET:
            Returns: All asset objects
    """
    # TODO: IMP Aug dict build (patch_asset)
    if request.method=='POST':
        try:
            # query dict collector
            query = {}
            # query dict padder (for empty values)
            param_list = ['name', 'image', 'tag', 'author', 'image_thumb', 'attached']
            for attri in request.args:
                query[attri] = request.args[attri]
                for param in param_list:
                    if param not in query:
                        query[param] = None

            asset = POST_asset(con, meta, **query)
            result = {
                'responce': 'successful',
                'location': ROUTE + '/asset/' + str(asset[0])
            }
            return make_response(jsonify({'POST: /asset': result})), 200

        except:
            fail = {'Action': 'failed'}
            return jsonify({'POST /asset': fail})

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
    # TODO: POST collections isnt working? Something todo with assets.
    # TODO: IMP Aug dict build (patch_asset)
    if request.method=='POST':
        try:
            # query dict collector
            query = {}
            # query dict padder (for empty values)
            param_list = ['name', 'image', 'tag', 'author', 'image_thumb', 'assets']
            for attri in request.args:
                query[attri] = request.args[attri]
                for param in param_list:
                    if param not in query:
                        query[param] = None
            print(query)
            collection = POST_collection(con, meta, **query,)
            result = {
                'responce': 'successful',
                'location': ROUTE + '/collection/' + str(collection[0])
            }
            return jsonify({'POST /Collection': result})

        except:
            fail = {'Action': 'failed'}
            return jsonify({'POST: /collection': fail})

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
    if request.method=='GET':
        session = Session()

        collectio_id = get_collection_by_id(session, collection_id)
    else:
        return jsonify({'collection': 'failed - endpoint only accepts GET methods'})
    return jsonify({'collection': collectio_id})


@app.route('{}/asset/<int:asset_id>'.format(ROUTE), methods=['GET'])
def get_asset_id(asset_id):
    if request.method=='GET':
        session = Session()
        asse_id = get_asset_by_id(session, asset_id)
    else:
        return jsonify({'asset': 'failed - endpoint only accepts GET methods'})
    return jsonify({'asset': asse_id})


@app.route('{}/query'.format(ROUTE), methods=['GET'])
def query():
    # TODO: refactor to function.
    # TODO: currently only one word can be search at a time.
    query = request.args.get('query')

    # convert query to list
    querylist = query.split(',')

    found_ids = []
    for term in querylist:
        # Query dev_asset
        # Build list of ids that match search terms.
        query_sql = con.execute("""SELECT array_agg(id) from asset where '{}' = ANY(tag)""".format(term))
        for i in query_sql:
            for x in i[0]:
                found_ids.append(x)

    return jsonify({'query': found_ids})


@app.route(
    '{}/collection/delete/<int:collection_id>'.format(ROUTE), methods=['DELETE']
    )
def delete_collection(collection_id):
    # TODO: Return flow control. currently its always successful.
    if request.method=='DELETE':
        collection_id = DELETE_collection(meta, collection_id)

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
    # TODO: Return flow control. currently its always successful.
    if request.method=='DELETE':
        asset_id = DELETE_asset(meta, asset_id)

        if asset_id:
            result = {
                'Action': 'successful',
                'asset id': 'IMP'
            }
            return jsonify({'DELETE asset/delete/': result})
        else:
            result = {
                'Action': 'fail',
                'asset id': 'IMP'
            }
            return jsonify({'DELETE asset/delete/': result})


@app.route('/glance/api/asset/patch', methods=['PATCH'])
def patch_asset():
    # TODO: Refactor to function
    # TODO: function should update moddate
    # TODO: IMP tag process
    query = {}
    # collect user entered data
    for attri in request.args:
        query[attri] = request.args[attri]

    if 'id' in query:
        for k, v in query.items():
            if k == 'id':
                pass
            elif k == 'tag':
                # TODO: process tags
                pass
            else:
                query_sql = con.execute(
                    """
                    UPDATE asset SET {} = '{}'
                    WHERE
                    ID = '{}'
                    """.format(k, v, query['id']))

    return jsonify({'PATCH': 'success'})


@app.route('{}/collection/patch'.format(ROUTE), methods=['PATCH'])
def patch_collection():
    # TODO: Refactor to function
    # TODO: function should update moddate
    query = {}
    # collect user entered data
    for attri in request.args:
        query[attri] = request.args[attri]

    if 'id' in query:
        for k, v in query.items():
            if k == 'id':
                pass
            elif k == 'tag':
                # TODO: process tags
                pass
            elif k == 'asset':
                # TODO: IMP asset patch
                pass
            else:
                query_sql = con.execute(
                    """
                    UPDATE asset SET {} = '{}'
                    WHERE
                    ID = '{}'
                    """.format(k, v, query['id']))

    return jsonify({'PATCH': 'success'})


"""
# Dev helpers
def RESET_DB(con, meta):
    drop_table(con, meta, 'dev_collection')
    drop_table(con, meta, 'asset')
    make_test_tables(con, meta)


def POP_DB(con, meta):
    POST_collection(con, meta)
    POST_asset(con, meta)
    POST_collection(con, meta)
    POST_asset(con, meta)
"""

# RESET_DB(con, meta)
# POP_DB(con, meta)
# tagss = ['a', 'couple', 'moraaade']
# PUT_asset_tag(con, meta, 1, ['foo', 'woo'])
# GET_asset(con, meta)
# print(GET_collection(con, meta))
# GET_collection_id(con, meta, 1)
# get_tables_db(meta)
# get_columns_(meta, 'dev_asset')


if __name__ == '__main__':
    app.run(debug=True)
