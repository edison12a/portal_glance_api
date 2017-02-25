import datetime
from ast import literal_eval

from sqlalchemy import Column, func, Integer, Table, String, ForeignKey, DateTime, JSON
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import cred

# Database models
Base = declarative_base()


assignment = Table('assignment', Base.metadata,
    Column('collection_id', Integer, ForeignKey('collection.id')),
    Column('asset_id', Integer, ForeignKey('asset.id'))
)

tag_table = Table('tag_table', Base.metadata,
    Column('tag_id', Integer, ForeignKey('tag.id')),
    Column('asset_id', Integer, ForeignKey('asset.id')),
    Column('collection_id', Integer, ForeignKey('collection.id'))
)


class Collection(Base):
    # TODO: Better repr
    __tablename__ = 'collection'



    id = Column(Integer, primary_key=True)
    name = Column(String)
    image = Column(String)
    image_thumb = Column(String)
    flag = Column(Integer, default=0)
    author = Column(String)
    initdate = Column(DateTime, default=func.now())
    moddate = Column(DateTime, default=func.now())
    item_type = Column(String, default=__tablename__)

    assets = relationship("Asset",
        secondary=assignment, back_populates="collections"
    )
    tags = relationship("Tag",
        secondary=tag_table
    )

    def __repr__(self):
        return "<Collection(name='%s', image='%s', assets='%s')>" % (
            self.name, self.image, self.assets
        )

class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    item = relationship('Asset',
        secondary=tag_table, back_populates='tags'
    )
    collection_tags = relationship('Collection',
        secondary=tag_table, back_populates='tags'
    )

    def __repr__(self):
        return "<Tag(name={})>".format(self.name)


class Asset(Base):
    # TODO: Better repr
    __tablename__ = 'asset'

    print(func.now())

    id = Column(Integer, primary_key=True)
    name = Column(String)
    image = Column(String)
    image_thumb = Column(String)
    attached = Column(String)
    flag = Column(Integer, default=0)
    author = Column(String)
    initdate = Column(DateTime, default=func.now())
    moddate = Column(DateTime, default=func.now())
    item_type = Column(String, default=__tablename__)

    collections = relationship("Collection",
        secondary=assignment
    )
    tags = relationship("Tag",
        secondary=tag_table
    )


    def __repr__(self):
        return "<Asset(id='%s', name='%s')>" % (
            self.id, self.name
        )


# private functions
def __reset_db(session, engine):
    """drops tables and rebuild"""
    # TODO: remove tables doesnt work
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

    print(data)

    # Database entry
    asset = Asset(
        name=data['name'], image=data['image'],
        image_thumb=data['image_thumb'], attached=data['attached'],
        author=data['author']
    )

    session.add(asset)

    if 'tags' in payload:
        tags = payload['tags'].split()
        for term in tags:
            newtag = Tag(name=term)
            asset.tags.append(newtag)


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

        # init tags
        item['tags'] = []
        try:
            bla = session.query(Collection).filter_by(id=collection.id).first().tags
            for x in bla:
                item['tags'].append(str(x.name))
        except:
            pass

        # init assets
        item['assets'] = []

        assignments = session.query(Collection).filter_by(
            id=collection.id
        ).first().assets

        for assignment in assignments:
            item['assets'].append(str(assignment))

        result.append(item)


    return result


def get_assets(session):
    """Returns all asset objects"""
    assets = []
    for asset in session.query(Asset).order_by(Asset.moddate):
        assets.append(asset)

    result = []
    # build asset item object for user
    for asset in assets:
        item = {}
        for column in asset.__table__.columns:
            item[column.name] = str(getattr(asset, column.name))

        # init collections
        item['collections'] = []
        koo = session.query(Asset).filter_by(id=asset.id).first().collections
        for x in koo:
            item['collections'].append(str(x))

        # init tags
        item['tags'] = []
        for x in asset.tags:
            item['tags'].append(x.name)

        result.append(item)

    return result


def get_asset_by_id(session, id):
    """Return asset object using id"""
    # TODO: Returns trunc dates. Should return whole date.
    asset_by_id = session.query(Asset).get(id)
    print(asset_by_id.initdate)

    if asset_by_id:
        # TODO: Below takes a row and converts to a dict. Make func?
        result = {}
        for column in asset_by_id.__table__.columns:
            result[column.name] = str(getattr(asset_by_id, column.name))

        # init collections
        result['collections'] = []
        koo = session.query(Asset).filter_by(id=asset_by_id.id).first().collections
        for x in koo:
            result['collections'].append(str(x))

        # init tags
        result['tags'] = []
        bla = session.query(Asset).filter_by(id=asset_by_id.id).first().tags
        for x in bla:
            result['tags'].append(str(x.name))

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

        for column in collection_by_id.__table__.columns:
            result[column.name] = str(getattr(collection_by_id, column.name))

        # init tags
        result['tags'] = []
        bla = collection_by_id.tags

        for x in bla:
            result['tags'].append(str(x.name))

        # init assets
        result['assets'] = []
        assignments = session.query(Collection).filter_by(
            id=collection_by_id.id
        ).first().assets

        for assignment in assignments:
            result['assets'].append(str(assignment))

    else:

        result = {}

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

    id = int(user_columns['id'])
    # Check user columns
    asset_columns = Asset.__table__.columns.keys()
    # compare user column data to database columns
    for k, v in user_columns.items():

        if k in asset_columns:
            # if match append user data to approved query variable
            query[k] = v
        elif k == 'collections':
            query[k] = v.split()
        elif k == 'tags':
            query['tags'] = v.split()
        else:
            pass

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

        elif k == 'tags':
            for tag in v:
                inputy = str(tag)
                newtag = Tag(name=inputy)
                asset.tags.append(newtag)

            session.add(newtag)

            # query for assets tags
            bla = session.query(Asset).filter_by(id=asset.id).first().tags

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

        elif k == 'collections':
            for collection_id in query['collections']:
                existingcollection = session.query(Collection).get(collection_id)
                asset.collections.append(existingcollection)

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
            query[k] = v.split()
        elif k == 'tags':
            query[k] = v.split()
        elif k == 'remove_assets':
            query[k] = v.split()

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
            for asset_id in v:
                # TODO: dont use try/except for control flow
                # TODO: figure out how to handle removeal of assets
                # myparent.children.remove(somechild)
                try:
                    newasset = session.query(Asset).get(int(asset_id))
                    collection.assets.append(newasset)
                except:
                    pass
        elif k == 'remove_assets':
            for asset_id in v:
                try:
                    removeasset = session.query(Asset).get(int(asset_id))
                    collection.assets.remove(removeasset)
                except:
                    pass

        elif k == 'tags':

            for x in v:
                test = Tag(name=str(x))
                session.add(test)

                collection.tags.append(test)

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
    print('whaaa')

    # myparent.children.remove(somechild)

    # session.query(Collection).filter(Collection.id=='{}'.format(collection_id)).delete()
    # session.commit()``

    return True
