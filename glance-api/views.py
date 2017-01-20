from flask import Flask, jsonify, request

from dev_tool import make_test_tables, get_tables_db, get_columns_, drop_table
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

# config
ROUTE = '/glance/api'

# Make connection and Metadata object
con, meta = connect(cred.username, cred.password, 'glance', cred.ip)

@app.route('{}'.format(ROUTE))
def api():
    info = {
        'End Points': {
            'POST': {
                '/asset': 'POST: new asset',
                '/collection': 'POST: new collection'
            }, 'GET': {
                '/asset': 'GET: All assets',
                '/asset/<int>': 'GET: Return asset by id',
                '/collection': 'GET: All collections',
                '/collection/<int>': 'GET: Return collection by id',
                '/query': 'GET: Return collections/assets based on query',

            }, 'PUT': {
                '/asset/put': 'PUT: Update asset',
                '/collection/put': 'PUT: Update collection',
            }, 'DELETE': {
                '/asset/delete/<int>': 'DELETE: Remove asset via id',
                '/collection/delete/<int>': 'DELETE: Remove collection via id',
            }
        },
        'Maintainers': {
            'Visualhouse': 'rory.jarrel@visualhouse.co'
        }
    }
    return jsonify({'Glance WebAPI': info})


@app.route('{}/asset'.format(ROUTE), methods=['POST', 'GET'])
def asset():
    """Endpoint that accepts POST and GET"""
    # TODO: IMP Aug dict build (patch_asset)
    if request.method=='POST':
        # Collect user paramaters, is there a better way?
        name = request.args.get('name')
        image = request.args.get('image')
        tag = request.args.get('tag')
        author = request.args.get('author')
        image_thumb = request.args.get('image_thumb')
        attached = request.args.get('attached')

        try:
            asset_info = (
                name, image, tag, author, image_thumb, attached
                )

            asset = POST_asset(con, meta, *asset_info,)
            result = {
                'Action': 'successful',
                'asset id': asset[0]
            }
            return jsonify({'POST: /asset': result})
        except:
            fail = {'Action': 'failed'}
            return jsonify({'POST: /asset': fail})

    elif request.method=='GET':
        assets = GET_asset(con, meta)
        print(assets)

        return jsonify({'assets': assets})
    else:
        return jsonify({'Asset': 'This endpoint only accepts POST, GET methods.'})


@app.route('{}/collection'.format(ROUTE), methods=['POST', 'GET'])
def collection():
    # TODO: IMP Aug dict build (patch_asset)
    if request.method=='POST':
        # Collect user paramaters, is there a better way?
        name = request.args.get('name')
        image = request.args.get('image')
        tag = request.args.get('tag')
        author = request.args.get('author')
        image_thumb = request.args.get('image_thumb')
        assets = request.args.get('assets')

        try:
            collection_info = (
                name, image, tag, author, image_thumb, assets
                )

            collection = POST_collection(con, meta, *collection_info, 'dev_collection',)
            result = {
                'Action': 'successful',
                'asset id': collection[0]
            }
            return jsonify({'Collection': result})

        except:
            fail = {'Action': 'failed'}
            return jsonify({'POST: /collection': fail})

    elif request.method=='GET':
        collections = GET_collection(con, meta)
        return jsonify({'collections': collections})

    else:
        return jsonify({'Asset': 'This endpoint only accepts POST, GET methods.'})


@app.route('{}/collection/<int:collection_id>'.format(ROUTE), methods=['GET'])
def get_collection_id(collection_id):
    if request.method=='GET':
        collection_id = GET_collection_id(con, meta, collection_id)
    else:
        return jsonify({'collection': 'failed - endpoint only accepts GET methods'})
    return jsonify({'collection': collection_id})


@app.route('{}/asset/<int:asset_id>'.format(ROUTE), methods=['GET'])
def get_asset_id(asset_id):
    if request.method=='GET':
        asset_id = GET_asset_id(con, meta, asset_id)
    else:
        return jsonify({'asset': 'failed - endpoint only accepts GET methods'})
    return jsonify({'asset': asset_id})


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
        query_sql = con.execute("""SELECT array_agg(id) from dev_asset where '{}' = ANY(tag)""".format(term))
        for i in query_sql:
            for x in i[0]:
                found_ids.append(x)

    return jsonify({'query': found_ids})


@app.route('{}/asset/put'.format(ROUTE), methods=['GET', 'PUT'])
def put_asset_tag():
    # TODO: IMP Aug dict build (patch_asset)
    # TODO: the way taglist is built is a bit flakey
    # TODO: re write with better names, consistantcy
    if request.method=='PUT' or request.method=='GET':

        asset_id = request.args.get('asset_id')
        asset_n = request.args.get('asset_n')
        # tags from querystring be separated with a comma -only- ','
        # e.g. test_tag,test,another_tag
        tag = request.args.get('tag')
        asset_i = request.args.get('asset_i')
        asset_a = request.args.get('asset_a')
        image_thumb = request.args.get('image_thumb')

        # Init structures
        taglist=[]

        if tag != None:
            taglist = tag.split(',')

        if asset_n != None:
            pass

        asset = PUT_asset_tag(
            con, meta, asset_id,  asset_n, asset_i, asset_a, taglist, image_thumb
            )
        return jsonify({'asset': asset})
    else:
        return jsonify({'fail': 'POST or GET only'})


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
                    UPDATE dev_asset SET {} = '{}'
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
                    UPDATE dev_collection SET {} = '{}'
                    WHERE
                    ID = '{}'
                    """.format(k, v, query['id']))

    return jsonify({'PATCH': 'success'})


# Dev helpers
def RESET_DB(con, meta):
    drop_table(con, meta, 'dev_collection')
    drop_table(con, meta, 'dev_asset')
    make_test_tables(con, meta)


def POP_DB(con, meta):
    POST_collection(con, meta)
    POST_asset(con, meta)
    POST_collection(con, meta)
    POST_asset(con, meta)

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
