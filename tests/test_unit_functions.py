import pytest
import requests

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from glance_api.packages import functions
from glance_api.packages import models

"""
# config
SERVER = 'http://127.0.0.1:5000'
ROUTE = '/glance/api'

# sqlite3 in memory
engine = create_engine('sqlite:///tests/sqlite_test_database.db')

# Init sessionmaker
Session = sessionmaker(bind=engine)

# make db
session = Session()
functions.__reset_db(session, engine)
"""

@pytest.fixture(scope='session')
def db_connect(request):
    # TODO: set up rollback on database, so it doesnt get deleted on every
    # test.
    engine = create_engine('sqlite:///tests/sqlite_test_database.db')

    try:
        meta = sqlalchemy.MetaData(engine)
        meta.reflect()
        meta.drop_all()
    except:
        pass
    try:
        models.Base.metadata.create_all(engine)
    except:
        pass

    # Init sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()

    return session

"""
# TODO: this fixture might have to do with producing a clean session? without
# deleting database?
@pytest.fixture
def db_session(request, connection):
    from transaction import abort
    trans = connection.begin()
    request.addfinalizer(trans.rollback)
    request.addfinalizer(abort)

    from foo.models import DBSession
    return DBSession
"""

def test__reset_db():
    pass


def test_make_dict():
    pass


def test_post_collection(db_connect):
    # test data
    test_data = {'name': 'test_collection_name'}
    test_function = functions.post_collection(db_connect, **test_data)

    # asserts
    testing_data = db_connect.query(models.Collection).get(test_function.id)
    assert testing_data.name == test_function.name


def test_post_asset(db_connect):
    # test data
    test_data = {'name':'test_asset_name', 'image': 'test_asset_image'}
    test_function = functions.post_asset(db_connect, **test_data)

    # asserts
    testing_data = db_connect.query(models.Asset).get(int(test_function.id))
    assert testing_data.name == test_function.name


def test_get_collections(db_connect):
    # test function
    test_data = models.Collection(name='test_collection_name')
    db_connect.add(test_data)
    db_connect.commit()
    test_function = functions.get_collections(db_connect)

    # asserts
    testing_data = db_connect.query(models.Collection).all()
    assert len(test_function) == len(testing_data)


def test_get_assets(db_connect):
    # test data
    test_data = models.Asset(name='test_asset_name')
    db_connect.add(test_data)
    db_connect.commit()
    # test function
    test_function = functions.get_assets(db_connect)

    # asserts
    testing_data = db_connect.query(models.Asset).all()
    assert len(test_function) == len(testing_data)


def test_get_asset_by_id(db_connect):
    # test data
    test_data = models.Asset(name='test_asset_name')
    db_connect.add(test_data)
    db_connect.commit()
    # test function
    test_function = functions.get_asset_by_id(db_connect, test_data.id)
    # asserts
    assert test_data.name == test_function.name


def test_get_collection_by_id(db_connect):
    # test data
    test_data = models.Collection(name='test_collection_name')
    db_connect.add(test_data)
    db_connect.commit()
    # test function
    test_function = functions.get_collection_by_id(db_connect, test_data.id)
    # asserts
    assert test_data.name == test_function.name


def test_get_query():
    pass


def test_get_query_flag():
    pass


def test_patch_asset():
    pass


def test_patch_collection():
    pass


def test_del_asset():
    pass


def test_del_collection():
    pass
