"""
This module contains all tests for glance_api.modules.functions.py
"""

import os

import pytest
import requests
import sqlalchemy

from glance_api.modules import functions
from glance_api.modules import models
from glance_api import api


# TODO: Finish testing Item 

@pytest.fixture(scope='session')
def connection(request):
    # TODO: Figure how to delete sqlite_test_database.db on tests finish
    # current its just gitingored
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
    trans = connection.begin()
    request.addfinalizer(trans.rollback)

    from glance_api.api import session
    return session


def test_Item_with_no_session():
    with pytest.raises(TypeError):
        functions.Item()


def test_Item_get_tags_from_query_returns_list(db_session):
    test_data = {'filter': 'image', 'filter_people': None, 'query': 'animal'}

    test_method = functions.Item(db_session)._get_tags_from_query(test_data)

    assert type(test_method) == list


def test_Item_get_tags_from_query_no_tags(db_session):
    test_data = {'filter': 'image', 'filter_people': None, 'query': 'TEST_TAGS'}

    test_method = functions.Item(db_session)._get_tags_from_query(test_data)

    assert len(test_method) == 0


def test_Item_get_tags_from_query_tags(db_session):
    test_query = {'filter': 'image', 'filter_people': None, 'query': ''}
    test_tags = ['TEST_TAG_ONE', 'TEST_TAG_TWO', 'TEST_TAG_THREE']

    for tag in test_tags:
        new_tag = models.Tag(name=tag)
        db_session.add(new_tag)

    test_method = functions.Item(db_session)._get_tags_from_query(test_query)

    assert len(test_method) == 3


def test_Item_get_filter_tags_returns_list(db_session):
    test_query = {'filter': 'image', 'filter_people': None, 'query': ''}
    test_tags = ['TEST_TAG_ONE', 'TEST_TAG_TWO', 'TEST_TAG_THREE']

    for tag in test_tags:
        new_tag = models.Tag(name=tag)
        db_session.add(new_tag)

    tags = db_session.query(models.Tag).all()
    test_method = functions.Item(db_session)._get_filter_tags(test_query, tags)


    assert type(test_method) == list


def test_Item_get_filter_tags_image_has_tags(db_session):
    test_tags = ['TEST_TAG_ONE', 'TEST_TAG_TWO', 'TEST_TAG_THREE']
    test_query = {'filter': 'image', 'filter_people': None, 'query': ' '.join(test_tags)}
    
    new_image = models.Image(name='test')
    for tag in test_tags:
        new_tag = models.Tag(name=tag)
        db_session.add(new_tag)

    get_tag = db_session.query(models.Tag).filter_by(name=test_tags[0]).first()
    new_image.tags.append(get_tag)
    db_session.add(new_image)

    test_new_tag = db_session.query(models.Tag).all()

    test_method = functions.Item(db_session)._get_filter_tags(test_query, test_new_tag)

    assert len(test_method) == 1


def test_Item_get_filter_tags_image_has_no_tags(db_session):
    test_tags = ['TEST_TAG_ONE', 'TEST_TAG_TWO', 'TEST_TAG_THREE']
    test_query = {'filter': 'image', 'filter_people': None, 'query': ' '.join(test_tags)}
    
    new_image = models.Image(name='test')
    db_session.add(new_image)

    for tag in test_tags:
        new_tag = models.Tag(name=tag)
        db_session.add(new_tag)

    test_new_tag = db_session.query(models.Tag).all()
    test_method = functions.Item(db_session)._get_filter_tags(test_query, test_new_tag)

    assert len(test_method) == 0


def test_Item_get_filter_tags_no_filter(db_session):
    test_tags = ['TEST_TAG_ONE', 'TEST_TAG_TWO', 'TEST_TAG_THREE']
    test_query = {'filter': None, 'filter_people': None, 'query': ' '.join(test_tags)}
    
    new_image = models.Image(name='test')
    new_footage = models.Footage(name='test')
    db_session.add(new_image)
    db_session.add(new_footage)

    for tag in test_tags:
        new_tag = models.Tag(name=tag)
        db_session.add(new_tag)

    get_tag_one = db_session.query(models.Tag).filter_by(name=test_tags[0]).first()
    get_tag_two = db_session.query(models.Tag).filter_by(name=test_tags[0]).first()

    new_image.tags.append(get_tag_one)
    new_footage.tags.append(get_tag_two)

    test_new_tag = db_session.query(models.Tag).all()
    test_method = functions.Item(db_session)._get_filter_tags(test_query, test_new_tag)

    assert len(test_method) == 2


def test_Item_get_filter_tags_if_people():
    pass


def test_Item_get():
    pass


def test_Item_delete():
    pass


def test_Item_post():
    pass


def test_Item_patch():
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