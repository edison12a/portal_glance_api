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
# TODO: Currently using sqlite3 database for tests, need to use postgres instead
# TODO: Figure out how to make test database in postgres programmically.

@pytest.fixture(scope='session')
def connection(request):
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


def test_Item_tags_from_queries_returns_type_list(db_session):
    test_data = {'filter': 'image', 'filter_people': None, 'query': 'animal'}

    test_method = functions.Item(db_session)._tags_from_queries(test_data)

    assert type(test_method) == list


def test_Item_tags_from_queries_no_tags(db_session):
    test_data = {'filter': 'image', 'filter_people': None, 'query': 'TEST_TAGS'}

    test_method = functions.Item(db_session)._tags_from_queries(test_data)

    assert len(test_method) == 0


def test_Item_tags_from_queries_tags(db_session):
    test_query = {'filter': 'image', 'filter_people': None, 'query': ''}
    test_tags = ['TEST_TAG_ONE', 'TEST_TAG_TWO', 'TEST_TAG_THREE']

    for tag in test_tags:
        new_tag = models.Tag(name=tag)
        db_session.add(new_tag)

    test_method = functions.Item(db_session)._tags_from_queries(test_query)

    assert len(test_method) == 3


def test_Item_tags_from_queries_query(db_session):
    test_query = {'filter': '', 'filter_people': None, 'query': 'querytag notfoundtag'}
    test_tags = ['_one', '_group', 'querytag', 'notfoundtag']

    for tag in test_tags:
        new_tag = models.Tag(name=tag)
        db_session.add(new_tag)

    test_method = functions.Item(db_session)._tags_from_queries(test_query)

    assert len(test_method) == 2


def test_Item_tags_from_queries_filter_people(db_session):
    test_query = {'filter': 'people', 'filter_people': '_one _group', 'query': 'none'}
    test_tags = ['_one', '_group', 'querytag', 'notfoundtag']

    for tag in test_tags:
        new_tag = models.Tag(name=tag)
        db_session.add(new_tag)

    test_method = functions.Item(db_session)._tags_from_queries(test_query)

    assert len(test_method) == 2


def test_Item_tags_from_queries_filter_people_and_query(db_session):
    test_query = {'filter': 'people', 'filter_people': '_one _group', 'query': 'querytag'}
    test_tags = ['_one', '_group', 'querytag', 'notfoundtag']

    for tag in test_tags:
        new_tag = models.Tag(name=tag)
        db_session.add(new_tag)

    test_method = functions.Item(db_session)._tags_from_queries(test_query)

    assert len(test_method) == 3


def test_Item_filter_tags_returns_list(db_session):
    test_query = {'filter': 'image', 'filter_people': None, 'query': ''}
    test_tags = ['TEST_TAG_ONE', 'TEST_TAG_TWO', 'TEST_TAG_THREE']

    for tag in test_tags:
        new_tag = models.Tag(name=tag)
        db_session.add(new_tag)

    tags = db_session.query(models.Tag).all()
    test_method = functions.Item(db_session)._filter_tags(test_query, tags)


    assert type(test_method) == list


def test_Item_filter_tags_image_has_tags(db_session):
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

    test_method = functions.Item(db_session)._filter_tags(test_query, test_new_tag)

    assert len(test_method) == 1


def test_Item_filter_tags_image_has_no_tags(db_session):
    test_tags = ['TEST_TAG_ONE', 'TEST_TAG_TWO', 'TEST_TAG_THREE']
    test_query = {'filter': 'image', 'filter_people': None, 'query': ' '.join(test_tags)}
    
    new_image = models.Image(name='test')
    db_session.add(new_image)

    for tag in test_tags:
        new_tag = models.Tag(name=tag)
        db_session.add(new_tag)

    test_new_tag = db_session.query(models.Tag).all()
    test_method = functions.Item(db_session)._filter_tags(test_query, test_new_tag)

    assert len(test_method) == 0


def test_Item_filter_tags_no_filter(db_session):
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
    test_method = functions.Item(db_session)._filter_tags(test_query, test_new_tag)

    assert len(test_method) == 2


def test_Item_get_id_does_not_exists(db_session):
    test_data = {'id': 999, 'query': None, 'filter_people': None}

    test_method = functions.Item(db_session).get(id=test_data['id'])

    assert test_method == None


# TODO: Figure out how to make a test database in postgres programically
# for the following tests.
"""
def test_Item_get_id_does_exists(db_session):
    test_data = {'id': 1, 'query': None, 'filter_people': None}

    new_item = models.Item(type='image')
    db_session.add(new_item)

    test_method = functions.Item(db_session).get(id=test_data['id'])

    assert test_method == True


def test_Item_delete():
    pass


def test_Item_post():
    pass


def test_Item_patch():
    pass

"""