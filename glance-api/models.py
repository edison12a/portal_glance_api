import datetime
from ast import literal_eval

from sqlalchemy import Column, Integer, String, ForeignKey, Date, JSON
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import cred

# Database models
Base = declarative_base()

class Collection(Base):
    # TODO: Better repr
    __tablename__ = 'collection'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    image = Column(String)
    image_thumb = Column(String)
    tag = Column(ARRAY(String))
    flag = Column(Integer, default=0)
    author = Column(String)
    initdate = Column(Date, default=datetime.datetime.utcnow())
    moddate = Column(Date, default=datetime.datetime.utcnow())
    # relational data
    assets = relationship(
        "Asset", backref='collection'
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
    # relational data
    collection_id = Column(Integer, ForeignKey('collection.id'))
    # collection = relationship("Collection", back_populates="assets")

    def __repr__(self):
        return "<Asset(id='%s', name='%s')>" % (
            self.id, self.name
        )


# private functions
def __reset_db(session, engine):
    """drops tables and rebuild"""
    session.close()
    try:
        Asset.__table__.drop(engine)
        Collection.__table__.drop(engine)
        print('Old tables removed')
    except:
        pass
    Base.metadata.create_all(engine)
    print('building new tables')

    return True


# public functions
def post_collection(session, **kwarg):
    """ POST: Collection"""
    # TODO: make pretty

    test = Collection(
        name=kwarg['name'], image=kwarg['image'], image_thumb='ooo.jpg',
        tag=kwarg['tag'], author=kwarg['author'],
    )

    if kwarg['image_thumb'] == None:
        test.image_thumb = 'default_cover.jpg'
    else:
        test.image_thumb = kwarg['image_thumb']

    session.add(test)
    session.commit()

    return test


def post_asset(session, **kwarg):
    """ POST: Asset"""
    # TODO: Once asset table is finished update this function.
    # Approved query
    # TODO: Figure out how to use arrays with ORM. i.e. collection_ids

    asset = Asset(
        name=kwarg['name'], image=kwarg['image'],
        image_thumb=kwarg['image_thumb'], attached=kwarg['attached'],
        author=kwarg['author']
    )

    # TODO: Figure out how to add tags to the db
    """
    try:
        tags = kwarg['tag'].split(',')
        asset.tag = tags
    except:
        pass
    """

    session.add(asset)
    session.commit()

    return asset


def get_collections(session):
    """Returns all collection objects"""
    collections = []
    for instance in session.query(Collection).order_by(Collection.id):
        collections.append(instance)

    result = []
    for collection in collections:
        result.append({
            'id': collection.id,
            'name': collection.name,
            'image': collection.image,
            'image_thumb': collection.image_thumb,
            'tag': collection.tag,
            'flag': collection.flag,
            'author': collection.author,
            'initdate': collection.initdate,
            'moddate': collection.moddate
        })

    return result


def get_assets(session):
    """Returns all asset objects"""
    assets = []
    for instance in session.query(Asset).order_by(Asset.id):
        assets.append(instance)

    result = []
    for asset in assets:
        result.append({
            'id': asset.id,
            'name': asset.name,
            'image': asset.image,
            'image_thumb': asset.image_thumb,
            'attached': asset.attached,
            'tag': asset.tag,
            'flag': asset.flag,
            'author': asset.author,
            'initdate': asset.initdate,
            'moddate': asset.moddate
        })


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
    collection_by_id = session.query(Collection).get(id)
    if collection_by_id:
        # TODO: Below takes a row and converts to a dict.
        result = {}
        for column in collection_by_id.__table__.columns:
            result[column.name] = str(getattr(collection_by_id, column.name))
    else:
        result = {}

    return result


def get_query(session, **query):
    """takes list of words and returns related objects"""
    # TODO: currently searching every table with every query term, multiple
    # searches. gotta be a better way. look into postgres joins?
    result = []
    assets = []
    query_id = []

    # query asset name
    for term in query['query']:
        bla = session.query(Asset).filter_by(name=term).all()
        for x in bla:
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

        # catch if query returns None
        try:
            for _id in query_sql:
                query_id.append(_id[0][0])
        except TypeError as e:
            print('{}, not found in tags'.format(term))

    # remove dups from id list
    query_id = list(set(query_id))

    # using ids query whole rows, and append to assets.
    for _id in query_id:
        get = session.query(Asset).get(int(_id))
        assets.append(get)

    # process all assets all all tables
    for asset in assets:
        # assets.append(asset)

        asset_dict = {}
        for column in asset.__table__.columns:
            asset_dict[column.name] = str(getattr(asset, column.name))

        result.append(asset_dict)

    return result


def get_query_flag(session, flag):

    assets = []
    for instance in session.query(Asset).filter(Asset.flag>=1).order_by(Asset.id):
        assets.append(instance)

    result = []
    for asset in assets:
        result.append({
            'id': asset.id,
            'name': asset.name,
            'image': asset.image,
            'image_thumb': asset.image_thumb,
            'attached': asset.attached,
            'tag': asset.tag,
            'flag': asset.flag,
            'author': asset.author,
            'initdate': asset.initdate,
            'moddate': asset.moddate
        })

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
            pass

        else:
            pass

    # patches append moddate automatically
    asset.moddate = datetime.datetime.utcnow()

    session.add(asset)
    session.commit()

    return asset


def patch_collection(session, id, **user_columns):
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
            # TODO: Test adding assets
            #collection.assets = query['assets']
            pass
        elif k == 'tag':
            # TODO: Tag logic
            collection.tag = v
        elif k == 'flag':
            if query['flag'] == 1:
                try:
                    collection.flag += 1
                except TypeError:
                    collection.flag = 0
                    collection.flag += 1
            elif query['flag'] == 0:
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
    session.query(Collection).filter(
        Collection.id=='{}'.format(collection_id)
    ).delete()
    session.commit()

    return True
