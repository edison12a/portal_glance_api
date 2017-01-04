import ast

from flask import Flask, jsonify, request

from dev_tool import make_test_tables, get_tables_db, get_columns_, drop_table
from api_func import (
    connect, POST_collection, POST_asset, GET_asset, GET_collection,
    GET_collection_id, GET_asset_id, DELETE_collection, PUT_asset_tag,
    DELETE_asset
    )
import cred

app = Flask(__name__)
# app.config.from_object('config')

# TODO: refactor - post, get, put, delete can be used all on the same URI -
# TODO: research - Should connect() be getting closed at someonepoint? Is it?
# TODO: Auth
# TODO: Global config?
# TODO: api tests

# Make connection and Metadata object
con, meta = connect(cred.username, cred.password, 'glance', cred.ip)

@app.route('/glance/api/asset', methods=['POST'])
def post_asset():
    if request.method=='POST':
        # Collect user paramaters, is there a better way?
        name = request.args.get('asset_n')
        image = request.args.get('asset_i')
        tag = request.args.get('tag')
        author = request.args.get('asset_a')
        image_thumb = request.args.get('image_thumb')
        attached = request.args.get('attached')
        # TODO: Converting string to list uging ast.literal_eval() is there a
        # better way? safer? Maybe at the database level?
        tag_string_to_list = ast.literal_eval(tag)

        asset_info = (
            name, image, tag_string_to_list, author, image_thumb, attached
            )
        #print('---------------------------')
        #print(asset_info)

        asset = POST_asset(con, meta, *asset_info, 'dev_asset',)
        return jsonify({'POST': asset})


@app.route('/glance/api/collection', methods=['POST'])
def post_collection():
    if request.method=='POST':
        # Collect user paramaters, is there a better way?
        name = request.args.get('asset_n')
        image = request.args.get('asset_i')
        tag = request.args.get('tag')
        author = request.args.get('asset_a')
        image_thumb = request.args.get('image_thumb')
        assets = request.args.get('assets')
        # TODO: Converting string to list uging ast.literal_eval() is there a
        # better way? safer? Maybe at the database level?
        tag_string_to_list = ast.literal_eval(tag)

        collection_info = (
            name, image, tag_string_to_list, author, image_thumb, assets
            )

        collection = POST_collection(con, meta, *collection_info, 'dev_collection',)
        return jsonify({'Collection': collection})


@app.route('/glance/api/asset', methods=['GET'])
def get_assets():
    assets = GET_asset(con, meta)
    return jsonify({'assets': assets})


@app.route('/glance/api/collection', methods=['GET'])
def get_collection():
    collections = GET_collection(con, meta)
    return jsonify({'collections': collections})


@app.route('/glance/api/collection/<int:collection_id>', methods=['GET'])
def get_collection_id(collection_id):
    collection_id = GET_collection_id(con, meta, collection_id)
    return jsonify({'collection': collection_id})


@app.route('/glance/api/asset/<int:asset_id>', methods=['GET'])
def get_asset_id(asset_id):
    asset_id = GET_asset_id(con, meta, asset_id)
    return jsonify({'asset': asset_id})


@app.route('/glance/api/query', methods=['GET'])
def query():
    username = request.args.get('username')
    return jsonify({'query': username})


@app.route('/glance/api/asset/put', methods=['GET', 'PUT'])
def put_asset_tag():
    # TODO: the way taglist is built is a bit flakey
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


@app.route('/glance/api/collection/delete/<int:collection_id>', methods=['DELETE'])
def delete_collection(collection_id):
    # TODO: Return flow control. currently its always successful.
    if request.method=='DELETE':
        collection_id = DELETE_collection(meta, collection_id)
        return jsonify({'delete': True})


@app.route('/glance/api/asset/delete/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id):
    # TODO: Return flow control. currently its always successful.
    if request.method=='DELETE':
        asset_id = DELETE_asset(meta, asset_id)
        return jsonify({'delete': True})

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
