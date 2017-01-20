from sqlalchemy import JSON, ARRAY, Column, DateTime, String, Integer, ForeignKey, func, Table
import datetime

def make_test_tables(con, meta):

    dev_collection = Table('dev_collection', meta,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String),
        Column('image', String),
        Column('image_thumb', String),
        Column('tag', ARRAY(String)),
        Column('flag', Integer),
        Column('author', String),
        Column('initdate', DateTime, default=datetime.datetime.utcnow()),
        Column('moddate', DateTime, default=datetime.datetime.utcnow()),
        Column('assets', ARRAY(String)),
        extend_existing=True
    )
    dev_asset = Table('dev_asset', meta,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String),
        Column('image', String),
        Column('image_thumb', String),
        Column('attached', String),
        Column('tag', ARRAY(String)),
        Column('flag', Integer),
        Column('author', String),
        Column('initdate', DateTime, default=datetime.datetime.utcnow()),
        Column('moddate', DateTime, default=datetime.datetime.utcnow()),
        extend_existing=True
    )
    # Create the above tables
    meta.create_all(con)

    return True


# funcs
def get_tables_db(meta):

    for table in meta.tables:
        print(table)


def get_columns_(meta, tablename):
    results = meta.tables[tablename]
    results.c
    for col in results.c:
        print(col)


def drop_table(con, meta, tablename):
    try:
        result = meta.tables[tablename]
        result.drop(con)
    except:
        print('Table drop error')
