import sqlite3
import uuid

from flask import Flask, jsonify
from flask_restful import reqparse, abort, Api, Resource, fields, marshal_with
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func

from config import settings
from modules import convert
from modules import models
from modules import functions

# Config
# init app and db
app = Flask(__name__)
# conn = sqlite3.connect('example.db')

# config
app.config['SQLALCHEMY_DATABASE_URI'] = settings.POSTGRES_DATABASE
engine = create_engine(settings.POSTGRES_DATABASE, echo=False)
api = Api(app, '/glance/v2')
# db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# Init sessionmaker
Session = sessionmaker(bind=engine)


'''development tools'''
# functions
# session = Session()
# functions.__reset_db(session, engine)
# functions.__drop_table(session, engine)
# functions.__create_table(session, engine)


# helpers
def resp(status=None, data=None, link=None, error=None, message=None):
    """Function im using to build responses"""
    # TODO: make better
    response = {
        'status': status, 'data': data, 'link': link,
        'error': error, 'message': message
    }

    remove_none = []

    for x in response:
        if response[x] == None:
            remove_none.append(x)

    for x in remove_none:
        del response[x]

    return response

# auth
# Basic HTTP auth
@auth.verify_password
def verify(username, password):
    account_details = {'username': username, 'password': password}

    session = Session()
    validate_account = functions.get_account(session, **account_details)
    session.close()

    return validate_account


# API resources
class Entry(Resource):
    @auth.login_required
    def get(self):
        session = Session()
        entry = {
            'name': 'glance api',
            'version': 'v2',
            'resources': '',
            'collections': session.query(func.count(models.Collection.id)).scalar(),
            'images': session.query(func.count(models.Image.id)).scalar(),
            'footage': session.query(func.count(models.Footage.id)).scalar(),
            'geometry': session.query(func.count(models.Geometry.id)).scalar(),
            'people': session.query(func.count(models.People.id)).scalar(),
            'tags': session.query(func.count(models.Tag.id)).scalar()
        }

        return entry, 200


class Accounts(Resource):
    @auth.login_required
    def get(self, id):
        session = Session()
        raw_account = session.query(models.Account).filter_by(id=id).first()
        session.close()

        response = resp(status='success', data=convert.jsonify((raw_account,)))
        return response, 200


    @auth.login_required
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('galleries', type=str, help='help text')
        args = parser.parse_args()

        raw_account = models.Account.query.filter_by(id=id).first()

        if raw_account != None:
            if 'galleries' in args and args['galleries'] != None:
                raw_gallery = Gallery.query.filter_by(id=args['galleries']).first()

                if raw_gallery != None:
                    raw_account.galleries.append(raw_gallery)
                    db.session.commit()

                    response = resp(
                        status='success', link='/accounts/{}'.format(raw_account.id)
                        ), 201

                    return response

                else:
                    return resp(error='no such gallery id')

            else:
                return resp(error='must enter gallery id')

        else:
            return resp(error='no such account id')


    @auth.login_required
    def delete(self, id):
        session = Session()
        raw_account = session.query(models.Account).filter_by(id=id).first()

        if auth.username() == raw_account.username:
            session.delete(raw_account)
            session.commit()

            response = resp(status='success', message='account successfully deleted')

            session.close()
            return response

        else:
            session.close()
            return resp(message='Account can only be if logged in as the same account.')


class AccountsL(Resource):
    @auth.login_required
    def get(self):
        session = Session()
        raw_account = session.query(models.Account).all()

        response = resp(data=convert.jsonify(raw_account), status='success')

        session.close()
        return response, 200


    def post(self):
        parser = reqparse.RequestParser()

        # accepted ARGs from api
        parser.add_argument('username', type=str, help='help text')
        parser.add_argument('password', type=str, help='help text')
        args = parser.parse_args()

        #process user input
        if args['username'] != None and args['password'] != None:
            session = Session()
            existing_account = session.query(models.Account).filter_by(username=args['username']).first()
            if existing_account:
                response = resp(error='Account name already exists', status='failed')

                session.close()
                return response, 400

            new_account = models.Account(username=args['username'], password=args['password'])
            session.add(new_account)
            session.commit()

            response = resp(
                data=convert.jsonify((new_account,)),
                link='/accounts/{}'.format(new_account.id),
                status='success'
            )

            session.close()
            return response, 201

        else:
            response = resp(error='No post data', status='failed')
            return response, 400


class Items(Resource):
    @auth.login_required
    def get(self, id):

        session = Session()
        raw_item = functions.Item(session).get(id)
        if raw_item:
            response = resp(status='success', data=convert.jsonify((raw_item,)))

            session.close()
            return response

        else:
            response = resp(status='failed', error='item id doesnt exist')
            session.close()
            return response

    @auth.login_required
    def put(self, id):
        parser = reqparse.RequestParser()

        # accepted ARGs from api
        parser.add_argument('id', type=str, help='help text')
        parser.add_argument('name', type=str, help='help text')
        parser.add_argument('item_loc', type=str, help='help text')
        parser.add_argument('item_thumb', type=str, help='help text')
        parser.add_argument('attached', type=str, help='help text')
        parser.add_argument('item_type', type=str, help='help text')
        parser.add_argument('tags', type=str, help='help text')
        parser.add_argument('items', type=str, help='help text')
        parser.add_argument('append_to_collection', type=str, help='help text')
        parser.add_argument('people_tags', type=str, help='help text')
        args = parser.parse_args()

        session = Session()

        put_item = functions.Item(session).patch(args)

        response = resp(status='success', data=convert.jsonify((put_item,)))

        session.close()
        return response


    @auth.login_required
    def delete(self, id):
        session = Session()
        raw_account = session.query(models.Account).filter_by(username=auth.username()).first()
        raw_item = session.query(models.Item).filter_by(id=id).first()

        if auth.username() == raw_account.username:
            session.delete(raw_item)
            session.commit()

            response = resp(status='success', message='item successfully deleted')

            session.close()
            return response

        else:
            session.close()
            return resp(message='Item can only be deleted by the account of the uploader.')


class ItemsL(Resource):
    @auth.login_required
    def get(self):
        session = Session()
        raw_items = functions.Item(session).get()
        if raw_items:

            response = resp(status='success', data=convert.jsonify(raw_items))

            session.close()
            return response

        else:
            response = resp(status='failed', error='nothing in database')

            session.close()
            return response

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()

        # accepted ARGs from api
        parser.add_argument('name', type=str, help='help text')
        parser.add_argument('item_loc', type=str, help='help text')
        parser.add_argument('item_thumb', type=str, help='help text')
        parser.add_argument('attached', type=str, help='help text')
        parser.add_argument('item_type', type=str, help='help text')
        parser.add_argument('tags', type=str, help='help text')
        parser.add_argument('items', type=str, help='help text')
        args = parser.parse_args()

        session = Session()
        args['author'] = auth.username()
        new_item = functions.Item(session).post(args)
        if new_item:
            response = resp(status='success', message='New item created', data=convert.jsonify((new_item,)))

            session.close()
            return response

        else:
            response=resp(status='failed', error='somethings wrong')


class Tags(Resource):
    @auth.login_required
    def get(self, id):
        pass


    @auth.login_required
    def put(self, id):
        pass


    @auth.login_required
    def delete(self, id):
        pass


class TagsL(Resource):
    @auth.login_required
    def get(self):
        pass

    @auth.login_required
    def post(self):
        pass


class Query(Resource):
    @auth.login_required
    def get(self):
        parser = reqparse.RequestParser()

        # accepted ARGs from api
        parser.add_argument('filter', type=str, help='help text')
        parser.add_argument('filter_people', type=str, help='help text')
        parser.add_argument('query', type=str, help='help text')
        args = parser.parse_args()

        session = Session()
        test = functions.get_query(session, args)

        response = resp(status='success', data=convert.jsonify(test))

        session.close()
        return response


# routes
api.add_resource(Entry, '/')
api.add_resource(Accounts, '/accounts/<id>')
api.add_resource(AccountsL, '/accounts')
api.add_resource(Items, '/items/<id>')
api.add_resource(ItemsL, '/items')
api.add_resource(Tags, '/tags/<id>')
api.add_resource(TagsL, '/tags')
api.add_resource(Query, '/query')


if __name__ == '__main__':
    app.run(debug=True, port=5050)
