"""
This module contains all tests for glance_api.modules.dev_functions.py
"""

import os

import pytest
import sqlalchemy

from glance_api.modules import dev_functions
from glance_api.modules import models
from glance_api import api


# TODO: Complete dev tests

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


def test_reset_db(db_session):
    pass


def test_drop_table(db_session):
    pass


def test_create_table(db_session):
    pass