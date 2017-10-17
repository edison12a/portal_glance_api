import os

import pytest
import sqlalchemy

from glance_api.modules import models
from glance_api import api


# TODO: Test association tables

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
    # from transaction import abort
    trans = connection.begin()
    request.addfinalizer(trans.rollback)

    from glance_api.api import session

    return session


def test_db_Account_Table(db_session):
    # test data
    test_data = {'username': 'test_username', 'password': 'test_password'}
    # new user
    test_user = models.Account(username=test_data['username'], password=test_data['password'])
    db_session.add(test_user)

    assert 1 == db_session.query(models.Account).count()

    # delete user
    test_user = db_session.query(models.Account).filter_by(username='test_username').first()
    db_session.delete(test_user)

    assert 0 == db_session.query(models.Account).count()


def test_db_Tag(db_session):
    #test data
    test_data = {'name': 'test_tag_name'}
    # new tag
    test_tag = models.Tag(name=test_data['name'])
    db_session.add(test_tag)

    assert 1 == db_session.query(models.Tag).count()

    # delete tag
    test_tag = db_session.query(models.Tag).filter_by(name=test_data['name']).first()
    db_session.delete(test_tag)

    assert 0 == db_session.query(models.Tag).count()


def test_db_Item(db_session):
    #test data
    test_data = ['image', 'footage', 'geometry', 'people', 'collection']

    # new item
    for item_type in test_data:
        test_item = models.Item(type=item_type)
        db_session.add(test_item)

    assert 5 == db_session.query(models.Item).count()

    # delete item
    for item_type in test_data:
        test_item = db_session.query(models.Item).filter_by(type=item_type).first()
        db_session.delete(test_item)

    assert 0 == db_session.query(models.Item).count()


def test_db_Image(db_session):
    # test data
    test_data = {
        'name': 'test_name', 'item_loc': 'test_item_loc', 
        'item_thumb': 'test_item_thumb', 'flag': 0,
        'author': 'test_author', 'item_type': 'image',
        'attached': 'test_attached'
    }

    test_item = models.Image(
        name=test_data['name'], item_loc=test_data['item_loc'], 
        item_thumb=test_data['item_thumb'], flag=test_data['flag'], 
        author=test_data['author'], item_type=test_data['item_type'], 
        attached=test_data['attached']
    )
    db_session.add(test_item)

    assert 1 == db_session.query(models.Item).count()
    assert 1 == db_session.query(models.Image).count()

    test_item = db_session.query(models.Image).filter_by(name=test_data['name']).first()
    db_session.delete(test_item)

    assert 0 == db_session.query(models.Item).count()
    assert 0 == db_session.query(models.Image).count()


def test_db_Footage(db_session):
    # test data
    test_data = {
        'name': 'test_name', 'item_loc': 'test_item_loc', 
        'item_thumb': 'test_item_thumb', 'flag': 0,
        'author': 'test_author', 'item_type': 'footage',
        'attached': 'test_attached'
    }

    test_item = models.Footage(
        name=test_data['name'], item_loc=test_data['item_loc'], 
        item_thumb=test_data['item_thumb'], flag=test_data['flag'], 
        author=test_data['author'], item_type=test_data['item_type'], 
        attached=test_data['attached']
    )
    db_session.add(test_item)

    assert 1 == db_session.query(models.Item).count()
    assert 1 == db_session.query(models.Footage).count()

    test_item = db_session.query(models.Footage).filter_by(name=test_data['name']).first()
    db_session.delete(test_item)

    assert 0 == db_session.query(models.Item).count()
    assert 0 == db_session.query(models.Footage).count()


def test_db_Geometry(db_session):
    # test data
    test_data = {
        'name': 'test_name', 'item_loc': 'test_item_loc', 
        'item_thumb': 'test_item_thumb', 'flag': 0,
        'author': 'test_author', 'item_type': 'geometry',
        'attached': 'test_attached'
    }

    test_item = models.Geometry(
        name=test_data['name'], item_loc=test_data['item_loc'], 
        item_thumb=test_data['item_thumb'], flag=test_data['flag'], 
        author=test_data['author'], item_type=test_data['item_type'], 
        attached=test_data['attached']
    )
    db_session.add(test_item)

    assert 1 == db_session.query(models.Item).count()
    assert 1 == db_session.query(models.Geometry).count()

    test_item = db_session.query(models.Geometry).filter_by(name=test_data['name']).first()
    db_session.delete(test_item)

    assert 0 == db_session.query(models.Item).count()
    assert 0 == db_session.query(models.Geometry).count()


def test_db_People(db_session):
    # test data
    test_data = {
        'name': 'test_name', 'item_loc': 'test_item_loc', 
        'item_thumb': 'test_item_thumb', 'flag': 0,
        'author': 'test_author', 'item_type': 'people',
        'attached': 'test_attached'
    }

    test_item = models.People(
        name=test_data['name'], item_loc=test_data['item_loc'], 
        item_thumb=test_data['item_thumb'], flag=test_data['flag'], 
        author=test_data['author'], item_type=test_data['item_type'], 
        attached=test_data['attached']
    )
    db_session.add(test_item)

    assert 1 == db_session.query(models.Item).count()
    assert 1 == db_session.query(models.People).count()

    test_item = db_session.query(models.People).filter_by(name=test_data['name']).first()
    db_session.delete(test_item)

    assert 0 == db_session.query(models.Item).count()
    assert 0 == db_session.query(models.People).count()


def test_db_Collection(db_session):
    # test data
    test_data = {
        'name': 'test_name', 'item_loc': 'test_item_loc', 
        'item_thumb': 'test_item_thumb', 'flag': 0,
        'author': 'test_author', 'item_type': 'collection',
        'attached': 'test_attached'
    }

    test_item = models.Collection(
        name=test_data['name'], item_loc=test_data['item_loc'], 
        item_thumb=test_data['item_thumb'], flag=test_data['flag'], 
        author=test_data['author'], item_type=test_data['item_type'], 
        attached=test_data['attached']
    )
    db_session.add(test_item)

    assert 1 == db_session.query(models.Item).count()
    assert 1 == db_session.query(models.Collection).count()

    test_item = db_session.query(models.Collection).filter_by(name=test_data['name']).first()
    db_session.delete(test_item)

    assert 0 == db_session.query(models.Item).count()
    assert 0 == db_session.query(models.Collection).count() 