import pytest
import requests

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from glance_api.modules import functions
from glance_api.modules import models


@pytest.fixture(scope='session')
def test_session(request):
    # TODO: set up rollback on database, so it doesnt get deleted on every
    # test.
    # TODO: IMP deletion of db after tests.
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

"""
def test_post_collection(test_session):
    # test data
    test_data = {'name': 'test_collection_name'}
    test_function = functions.post_collection(test_session, **test_data)

    # asserts
    testing_data = test_session.query(models.Collection).get(test_function.id)
    assert testing_data.name == test_function.name


def test_post_asset(test_session):
    # test data
    test_data = {'name':'test_asset_name', 'image': 'test_asset_image'}
    test_function = functions.post_asset(test_session, **test_data)

    # asserts
    testing_data = test_session.query(models.Asset).get(int(test_function.id))
    assert testing_data.name == test_function.name


def test_get_collections(test_session):
    # test function
    test_data = models.Collection(name='test_collection_name')
    test_session.add(test_data)
    test_session.commit()
    test_function = functions.get_collections(test_session)

    # asserts
    testing_data = test_session.query(models.Collection).all()
    assert len(test_function) == len(testing_data)


def test_get_assets(test_session):
    # test data
    test_data = models.Asset(name='test_asset_name')
    test_session.add(test_data)
    test_session.commit()
    # test function
    test_function = functions.get_assets(test_session)

    # asserts
    testing_data = test_session.query(models.Asset).all()
    assert len(test_function) == len(testing_data)


def test_get_asset_by_id(test_session):
    # test data
    test_data = models.Asset(name='test_asset_name')
    test_session.add(test_data)
    test_session.commit()
    # test function
    test_function = functions.get_asset_by_id(test_session, test_data.id)
    # asserts
    assert test_data.name == test_function.name


def test_get_collection_by_id(test_session):
    # test data
    test_data = models.Collection(name='test_collection_name')
    test_session.add(test_data)
    test_session.commit()
    # test function
    test_function = functions.get_collection_by_id(test_session, test_data.id)
    # asserts
    assert test_data.name == test_function.name


def test_get_query(test_session):
    # TODO: Only testing assets at the moment.
    # test data
    # objects
    test_data_asset = models.Asset(name='test_asset_name')
    # tags
    test_tag_asset = models.Tag(name='testtagasset')

    test_session.add(test_data_asset)
    test_session.add(test_tag_asset)
    test_tag_data = {'query': [test_tag_asset.name]}
    # append tags to objects
    test_data_asset.tags.append(test_tag_asset)

    test_session.add(test_data_asset)
    test_session.commit()

    # test function
    test_function = functions.get_query(test_session, {'query': 'testtagasset'})
    # asserts
    assert len(test_function) == 1


def test_get_query_flag(test_session):
    # test data
    test_data = models.Asset(name='test_asset_name', flag=1)
    test_session.add(test_data)
    test_session.commit()
    # testing data
    testing_data = test_session.query(models.Asset).filter(int(flag)>0).all()
    # asserts
    assert len(testing_data) == 1


def test_patch_asset():
    pass


def test_patch_collection():
    pass


def test_del_asset(test_session):
    # test data
    test_data = models.Asset(name='test_asset_name')
    test_session.add(test_data)
    test_session.commit()
    # asserts
    # First test that the asset has been entered into the database.
    assert test_session.query(models.Asset).get(test_data.id).id == test_data.id
    # test function
    test_function = functions.del_asset(test_session, test_data.id)
    # final test to see if asset has been removed from database.
    assert test_session.query(models.Asset).get(test_data.id) == None


def test_del_collection(test_session):
    # test data
    test_data = models.Collection(name='test_collection_name')
    test_session.add(test_data)
    test_session.commit()
    # asserts
    # First test that the asset has been entered into the database.
    assert test_session.query(models.Collection).get(test_data.id).id == test_data.id
    # test function
    test_function = functions.del_collection(test_session, test_data.id)
    # final test to see if asset has been removed from database.
    assert test_session.query(models.Collection).get(test_data.id) == None

"""