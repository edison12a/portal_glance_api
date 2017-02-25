import datetime
from ast import literal_eval

from sqlalchemy import Column, Integer, Table, String, ForeignKey, Date, JSON
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import cred

# Database models
Base = declarative_base()


"""

class Parent(Base):
    __tablename__ = 'left'
    id = Column(Integer, primary_key=True)
    children = relationship(
        "Child",
        secondary=association_table,
        back_populates="parents")

class Child(Base):
    __tablename__ = 'right'
    id = Column(Integer, primary_key=True)
    parents = relationship(
        "Parent",
        secondary=association_table,
        back_populates="children")

"""




assignment = Table('assignment', Base.metadata,
    Column('collection_id', Integer, ForeignKey('collection.id')),
    Column('asset_id', Integer, ForeignKey('asset.id'))
)


class Collection(Base):
    # TODO: Better repr
    __tablename__ = 'collection'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    image = Column(String)
    image_thumb = Column(String)
    tag = Column(ARRAY(String), default=[])
    flag = Column(Integer, default=0)
    author = Column(String)
    initdate = Column(Date, default=datetime.datetime.utcnow())
    moddate = Column(Date, default=datetime.datetime.utcnow())
    item_type = Column(String, default=__tablename__)
    # relational data
    assets = relationship("Asset",
        secondary=assignment, back_populates="collections"
    )

    def __repr__(self):
        return "<Collection(name='%s', image='%s', assets='%s')>" % (
            self.name, self.image, self.assets
        )


class Asset(Base):
    # TODO: Better repr
    __tablename__ = 'asset'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    image = Column(String)
    image_thumb = Column(String)
    attached = Column(String)
    tag = Column(ARRAY(String), default=[])
    flag = Column(Integer, default=0)
    author = Column(String)
    initdate = Column(Date, default=datetime.datetime.utcnow())
    moddate = Column(Date, default=datetime.datetime.utcnow())
    item_type = Column(String, default=__tablename__)
    # relational data
    collections = relationship("Collection",
    secondary=assignment, back_populates="assets"
    )


    def __repr__(self):
        return "<Asset(id='%s', name='%s')>" % (
            self.id, self.name
        )


# private functions
def __reset_db(session, engine):
    """drops tables and rebuild"""
    session.close()
    try:
        assignment.__table__.drop(engine)
        Collection.__table__.drop(engine)
        Asset.__table__.drop(engine)
        print('Old tables removed')
    except:
        pass
    Base.metadata.create_all(engine)
    print('building new tables')

    return True


# public functions
def post_collection(session, **kwarg):
    """Posts collection to the database"""
    payload = {}
    data = {}

    for k, v in kwarg.items():
        payload[k] = v[0]

    for column in Collection.__table__.columns:
        if column.name in payload:
            data[column.name] = payload[column.name]
        elif column.name not in payload:
            data[column.name] = None
        else:
            pass

    collection = Collection(
        name=data['name'], image=data['image'], author=data['author']
    )

    if data['image_thumb'] == None:
        collection.image_thumb = 'default_cover.jpg'
    else:
        collection.image_thumb = data['image_thumb']

    session.add(collection)
    session.commit()

    return collection


def post_asset(session, **kwarg):
    """Posts asset to the database"""
    payload = {}
    data = {}

    # process user input
    for k, v in kwarg.items():
        payload[k] = v[0]

    # remove attri that arnt in the database
    for column in Asset.__table__.columns:
        if column.name in payload:
            data[column.name] = payload[column.name]
        elif column.name not in payload:
            data[column.name] = None
        else:
            pass

    # Database entry
    asset = Asset(
        name=data['name'], image=data['image'],
        image_thumb=data['image_thumb'], attached=data['attached'],
        author=data['author']
    )

    session.add(asset)
    session.commit()

    return asset


def get_collections(session):
    """Returns all collection objects"""
    collections = []
    for collection in session.query(Collection).order_by(Collection.id):
        collections.append(collection)

    result = []
    for collection in collections:
        item = {}
        for column in collection.__table__.columns:
            item[column.name] = str(getattr(collection, column.name))

        item['tag'] = literal_eval(item['tag'])
        item['assets'] = []

        koo = session.query(Collection).filter_by(id=collection.id).first().assets
        for x in koo:
            item['assets'].append(str(x))

        # session.query(Collection).filter(Collection.assets.any(collection_id=collection.id)).all()


        result.append(item)
        #append collections to 'assets'



    return result


def get_assets(session):
    """Returns all asset objects"""
    assets = []
    for asset in session.query(Asset).order_by(Asset.moddate):
        assets.append(asset)

    result = []
    for asset in assets:
        item = {}
        for column in asset.__table__.columns:
            item[column.name] = str(getattr(asset, column.name))
        item['tag'] = literal_eval(item['tag'])
        result.append(item)

        # koo = session.query(Asset).filter_by(id=asset.id).first()
        # print(koo)



    return result


def get_asset_by_id(session, id):
    """Return asset object using id"""
    # TODO: Returns trunc dates. Should return whole date.
    asset_by_id = session.query(Asset).get(id)

    if asset_by_id:
        # TODO: Below takes a row and converts to a dict. Make func?
        result = {}
        for column in asset_by_id.__table__.columns:
            result[column.name] = str(getattr(asset_by_id, column.name))
    else:
        result = {}

    return result


def get_collection_by_id(session, id):
    """Returns collection object using id"""
    # TODO: Returns trunc dates. Should return whole date.
    # TODO: Figure out a better way to set collections assets.
    collection_by_id = session.query(Collection).get(id)

    # if collection exists, get item
    if collection_by_id:
        result = {}
        result['assets'] = []

        for column in collection_by_id.__table__.columns:
            result[column.name] = str(getattr(collection_by_id, column.name))

    else:

        result = {}

    """
    # get all assets associated with collection
    assets = session.query(Asset).filter_by(collection_id=id).all()
    # process and append assets to return item
    for asset in assets:
        asset_item = {}
        for column in asset.__table__.columns:
            asset_item[column.name] = str(getattr(asset, column.name))

        result['assets'].append(asset_item)
    """
    return result


def get_query(session, userquery):
    """takes list of words and returns related objects"""
    # TODO: currently searching every table with every query term, multiple
    # searches. gotta be a better way. look into postgres joins?
    result = []
    assets = []
    query_id = []
    collection_id = []

    for k, v in userquery.items():
        query = {k: str(v).split()}

    for term in query['query']:
        # query asset names
        for x in session.query(Asset).filter_by(name=term).all():
            try:
                assets.append(x)
            except:
                pass
        # query collection name
        for x in session.query(Asset).filter_by(name=term).all():
            try:
                assets.append(x)
            except:
                pass

    # query asset tag
    # TODO: Figure out a better way to search tags. currently it finds tags, ids
    # returns ids to list, then query each id to get item details.
    for term in query['query']:
        query_sql = session.execute(
            """SELECT array_agg(id) from asset where '{}' = ANY(tag)""".format(
                term
            )
        )

        query_collection_sql = session.execute(
            """SELECT array_agg(id) from collection where '{}' = ANY(tag)""".format(
                term
            )
        )

        # catch if asset query returns None
        try:
            for _id in query_sql:
                query_id.append(_id[0][0])
        except TypeError as e:
            print('{}, not found in asset tags'.format(term))

        # catch if collection query returns None
        try:
            for _id in query_collection_sql:
                collection_id.append(_id[0][0])
        except TypeError as e:
            print('{}, not found in collection tags'.format(term))

    # remove dups from id list
    query_id = list(set(query_id))
    collection_id = list(set(collection_id))

    # using ids query whole rows, and append to assets.
    for _id in query_id:
        get = session.query(Asset).get(int(_id))
        assets.append(get)

    for _id in collection_id:
        get = session.query(Collection).get(int(_id))
        assets.append(get)

    # process all assets all all tables
    for asset in assets:
        item = {}
        for column in asset.__table__.columns:
            item[column.name] = str(getattr(asset, column.name))

        result.append(item)

    return result


def get_query_flag(session, flag):
    """ Returns list of flagged items """
    assets = []
    for instance in session.query(Asset).filter(Asset.flag>=1).order_by(Asset.id):
        assets.append(instance)

    for instance in session.query(Collection).filter(Collection.flag>=1).order_by(Collection.id):
        assets.append(instance)

    result = []
    for asset in assets:
        if asset.item_type == 'asset':
            item = {}
            for column in asset.__table__.columns:
                item[column.name] = str(getattr(asset, column.name))
            result.append(item)

        elif asset.item_type == 'collection':
            item = {}
            for column in asset.__table__.columns:
                item[column.name] = str(getattr(asset, column.name))
            result.append(item)

    return result


def get_query_tag(session):

    # bla = session.query(Asset).filter(Asset.tag).all()
    hrr = session.query(Asset).order_by(Asset.id)

    return 'bla'


def patch_assety(session, **user_columns):
    """patches users defined columns with user defined values"""
    # TODO: catch error - if asset id doesnt exist.
    # TODO: patch tag doesnt work, should append, instead it overwrites
    query = {}
    print(user_columns)
    id = int(user_columns['id'])
    # Check user columns
    asset_columns = Asset.__table__.columns.keys()
    # compare user column data to database columns
    for k, v in user_columns.items():
        if k in asset_columns:
            # if match append user data to approved query variable
            query[k] = v
        else:
            pass

    # query logical for appendind fields
    asset = session.query(Asset).get(id)

    for k, v in query.items():
        if k == 'name':
            asset.name = v

        elif k == 'image':
            asset.image = v

        elif k == 'image_thumb':
            asset.image_thumb = v

        elif k == 'attached':
            asset.attached = v

        elif k == 'tag':
            # TODO: Tag logic
            # TODO: shouldnt be using literal_eval. fix in model.

            # asset.update().where(Asset.id == 1).values(tag=['testpoo'])

            conv = literal_eval(v)
            asset.tag = conv

        elif k == 'flag':
            if int(query['flag']) == 1:
                try:
                    asset.flag += 1
                except TypeError:
                    asset.flag = 0
                    asset.flag += 1
            elif int(query['flag']) == 0:
                asset.flag -= 1
            else:
                pass

        elif k == 'collection_id':
            # TODO: IMP many-to-many for collections and tags?
            asset.collection_id = int(v)
            pass

        else:
            pass


    # patches append moddate automatically
    asset.moddate = datetime.datetime.utcnow()

    session.add(asset)
    session.commit()

    return asset


def patch_collectiony(session, id, **user_columns):
    """patches users defined columns with user defined values"""
    query = {}
    # Check user columns
    collection_columns = Collection.__table__.columns.keys()
    # compare user column data to database columns
    for k, v in user_columns.items():
        if k in collection_columns:
            # if match append user data to approved query variable
            query[k] = v

        else:
            pass
        if k == 'assets':
            query[k] = v


    # query logical for appendind fields
    collection = session.query(Collection).get(id)
    for k, v in query.items():
        if k == 'name':
            collection.name = v
        elif k == 'image':
            collection.image = v
        elif k == 'image_thumb':
            collection.image_thumb = v
        elif k == 'assets':
            # query assets and append to collection
            # TODO: remove try/except
            try:
                newasset = session.query(Asset).get(int(v))
                collection.assets.append(newasset)
            except:
                print('query asset error')

            # all_ = session.query(Collection).filter_by(id=collection.id).first().assets

        elif k == 'tag':
            # TODO: Tag logic
            # TODO: shouldnt be using literal_eval. fix in model.

            # asset.update().where(Asset.id == 1).values(tag=['testpoo'])

            conv = literal_eval(v)
            collection.tag = conv

        elif k == 'flag':
            if int(query['flag']) == 1:
                try:
                    collection.flag += 1
                except TypeError:
                    collection.flag = 0
                    collection.flag += 1
            elif int(query['flag']) == 0:
                collection.flag -= 1
            else:
                pass
        else:
            pass

    # patches append moddate automatically
    collection.moddate = datetime.datetime.utcnow()

    session.add(collection)
    session.commit()



    return collection


def delete_assety(session, asset_id):
    # TODO: doc strings
    session.query(Asset).filter(Asset.id=='{}'.format(asset_id)).delete()
    session.commit()

    return True


def delete_collectiony(session, collection_id):
    # TODO: doc strings
    session.query(Collection).filter(Collection.id=='{}'.format(collection_id)).delete()
    session.commit()

    return True
