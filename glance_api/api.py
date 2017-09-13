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
import modules.functions as functions

app = Flask(__name__)

# database
engine = create_engine(settings.POSTGRES_DATABASE, echo=False)

# Init sessionmaker
Session = sessionmaker(bind=engine)

"""
'''development tools'''
# functions
session = Session()
functions.__reset_db(session, engine)
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

        session = Session()
        posted_user = functions.post_user(session, **post_data)
        session.close()

        return jsonify({'user': str(type(posted_user))})

    elif request.method=='GET':
        user_details = {}

        username = request.args.get('username')
        password = request.args.get('password')

        session = Session()

        user_details['username'] = username
        user_details['password'] = password

        user_cred = functions.get_user(session, **user_details)

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
        test = functions.Item(session).post(query)
        result = functions.to_dict((test,))
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
            raw_items = functions.Item(session).get(filter=request.args['filter'])
            result = functions.to_dict(raw_items)
        else:
            raw_items = functions.Item(session).get()
            result = functions.to_dict(raw_items)

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
        # sorts items by initdate
        result.sort(key=lambda r: r["initdate"], reverse=True)

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
    result = functions.get_tag(session, data)
    session.close()

    return jsonify({'tags': result})


# queries
@app.route('{}/query'.format(settings.ROUTE), methods=['GET'])
def query():
    """ returns results from querys
    'flag': takes key/value, returns
    'query': takes list of string, returns list of dict
    'filter': takes str, affects 'query'
    'filter_people': ???
    """
    if 'flag' in request.args:
        pass

    elif 'query' in request.args:
        # TODO: For some reason `functions.get_query()` only accepts a dict?
        session = Session()
        raw_items = functions.get_query(session, request.args)
        items = functions.to_dict(raw_items)
        # sorts items by date
        items.sort(key=lambda r: r["initdate"], reverse=True)

        session.close()

        return jsonify({'result': items})

    return jsonify({'result': ''})


@app.route('{}/collection/author/<author>'.format(settings.ROUTE))
def get_collection_author(author):
    session = Session()

    raw_result = functions.get_collection_by_author(session, author)
    result = functions.to_dict(raw_result)

    session.close()

    return jsonify({'result': result})


@app.route('{}/item/<int:item_id>'.format(settings.ROUTE), methods=['GET'])
def get_item(item_id):
    # TODO: Doc string
    if request.method=='GET':
        session = Session()
        raw_asset = functions.Item(session).get(item_id)
        asset = functions.to_dict((raw_asset, ))

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
        asset = functions.Item(session).delete(asset_id)

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

    patch_data = {}
    for y in request.args:
        patch_data[y] = request.args[y]

    session = Session()
    raw_item = functions.Item(session).patch(patch_data)
    item = functions.to_dict((raw_item,))
    session.close()

    return jsonify({'PATCH': item})



if __name__ == '__main__':
    app.run(debug=True, port=5050)
