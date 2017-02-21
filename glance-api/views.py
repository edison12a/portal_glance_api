from flask import Flask, jsonify, request, make_response

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# from dev_tool import get_tables_db, get_columns_, drop_table
from models import (
    __reset_db, get_collections, get_assets, get_collection_by_id,
    get_asset_by_id, get_query, post_collection, post_asset, delete_assety,
    delete_collectiony, patch_assety, get_query_flag
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
__reset_db(session, engine)
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
            param_list = [
                'name', 'image', 'tag', 'author', 'image_thumb', 'attached',
            ]
            for attri in request.args:
                query[attri] = request.args[attri]
                for param in param_list:
                    if param not in query:
                        query[param] = None




            session = Session()

            asset = post_asset(session, **query)

            result = {
                'responce': 'successful',
                'location': ROUTE + '/asset/' + str(asset.id)
            }
            session.close()
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
    # TODO: make pretty.
    if request.method=='POST':

        # query dict collector
        query = {}
        # query dict padder (for empty values)
        param_list = ['name', 'image', 'tag', 'author', 'image_thumb', 'assets']
        for attri in request.args:
            query[attri] = request.args[attri]
            for param in param_list:
                if param not in query:
                    query[param] = None

        session = Session()
        bla = post_collection(session, **query)

        result = {
            'responce': 'successful',
            'location': ROUTE + '/collection/' + str(bla.id)
        }
        session.close()


        return make_response(jsonify({'POST: /asset': result})), 200


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

        return jsonify({'flagged assets': flagged})

    elif 'query' in request.args:
        # TODO: figure how best way to apply used to query and filter.
        query = {'query': request.args['query'].split()}

        session = Session()
        assets = get_query(session, **query)

        session.close()

        found_ids = []

    return jsonify({'result': assets})


@app.route(
    '{}/collection/delete/<int:collection_id>'.format(ROUTE), methods=['DELETE']
    )
def delete_collection(collection_id):
    # TODO: make better responce
    if request.method=='DELETE':
        session = Session()
        asset = delete_collectiony(session, collection_id)

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


@app.route('/glance/api/asset/patch', methods=['PATCH'])
def patch_asset():
    # TODO: impletement with sqlalchemy session
    patch_data = {}
    for x in request.args:
        patch_data[x] = request.args.get(x)

    print(patch_data)

    session = Session()
    try:
        bla = patch_assety(session, **patch_data)
    except:
        pass
    session.close()

    return jsonify({'PATCH': 'NO IMP'})


@app.route('{}/collection/patch'.format(ROUTE), methods=['PATCH'])
def patch_collection():
    # TODO: impletement with sqlalchemy session
    return jsonify({'PATCH': 'NO IMP'})



if __name__ == '__main__':
    app.run(debug=True)
