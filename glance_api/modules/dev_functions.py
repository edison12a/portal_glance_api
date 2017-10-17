"""
This module contains development functions for glance api
"""

import glance_api.modules.models


# development functions
# TODO: dev functions should be their own module.
def __reset_db(session, engine):
    """DANGER: Drops and rebuilds all tables, if built declaritvely.

    :param session: 'sqlalchemy.orm.session.Session'.
    :param engine: sqlalchemy engine object.

    :return type: bool
    """
    # TODO: make better.
    session.close()

    try:
        import sqlalchemy
        meta = sqlalchemy.MetaData(engine)
        meta.reflect()
        meta.drop_all()
    except:
        print('----------------------------')
        print('Table have not been deleted.')
        print('----------------------------')
    try:
        glance_api.modules.models.Base.metadata.create_all(engine)
    except:
        print('---------------------------')
        print('Tables have not been built.')
        print('---------------------------')

    print('----------------------------------------')
    print('Tables removed, and re-built successful.')
    print('----------------------------------------')

    # TODO: is return True 'pythonic', something better?
    return True


def __drop_table(session, engine):
    session.close()
    glance_api.modules.models.Account.__table__.drop(engine)


def __create_table(session, engine):
    session.close()
    glance_api.modules.models.Account.__table__.create(engine)

