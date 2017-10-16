import os

import pytest
import requests
import sqlalchemy

from glance_api.modules import functions
from glance_api.modules import models
from glance_api import api


print(os.getcwd())
@pytest.fixture(scope='session')
def connection(request):
    # TODO: Figure how to delete sqlite_test_database.db on tests finish
    db_name = 'sqlite_test_database.db'
    engine = sqlalchemy.create_engine(f'sqlite:///tests/{db_name}')
    models.Base.metadata.create_all(engine)
    connection = engine.connect()
    api.session.registry.clear()
    api.session.configure(bind=connection)
    models.Base.metadata.bind = engine
    request.addfinalizer(models.Base.metadata.drop_all)

    return connection

@pytest.fixture
def db_session(request, connection):
    # from transaction import abort
    trans = connection.begin()
    request.addfinalizer(trans.rollback)
    request.addfinalizer(models.Base.metadata.drop_all)

    from glance_api.api import session
    return session


def test_db_is_rolled_back(db_session):
    print(os.getcwd())
    assert 0 == db_session.query(models.Account).count()

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