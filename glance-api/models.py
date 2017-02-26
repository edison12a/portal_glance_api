# TODO: Clean up imports, ast, datetime?
# TODO: Implement proper config, include auth to replace 'import cred'
import datetime
from ast import literal_eval

from sqlalchemy import Column, func, Integer, Table, String, ForeignKey, DateTime, JSON
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import cred


# TODO: Model / function logic code is getting big. need to split into different
# modules

"""postgrest/sqlalchemy database design"""
# Database models
Base = declarative_base()

"""association tables"""
# association table: Collection.id, Asset.id
assignment = Table('assignment', Base.metadata,
    Column('collection_id', Integer, ForeignKey('collection.id')),
    Column('asset_id', Integer, ForeignKey('asset.id'))
)

# association table: Tag.id, Asset.id, Collection.id
# TODO: I think many-to-manys should link 3 classes? perhaps theres a better way
# maybe an additional 'all objects table' so everything have a unique id?
tag_table = Table('tag_table', Base.metadata,
    Column('tag_id', Integer, ForeignKey('tag.id')),
    Column('asset_id', Integer, ForeignKey('asset.id')),
    Column('collection_id', Integer, ForeignKey('collection.id'))
)


"""declarative tables"""
class Collection(Base):
    """Collection Database structure, declarative"""
    # TODO: Better repr
    # TODO: read more on the back_populates/backref stuff
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
        return "<Collection(name='%s', image='%s')>" % (
            self.name, self.image
        )


class Tag(Base):
    """Tag database structure, declarative"""
    # TODO: I think all asset databases should be replaced with a 'all assets'
    # table.
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
    """Asset database structure, declarative"""
    # TODO: Better repr
    __tablename__ = 'asset'

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


"""database methods"""
# dev functions
def __reset_db(session, engine):
    """DEV: drops tables and rebuild"""
    # TODO: remove tables doesnt work, need to figure out how to 'drop cascade'
    # close any open session.
    session.close()
    # TODO: remove try/except for EXISTS, code flow etc.
    try:
        assignment.__table__.drop(engine)
        Collection.__table__.drop(engine)
        Asset.__table__.drop(engine)
        print('Old tables removed')
    except:
        pass
    Base.metadata.create_all(engine)
    print('building new tables')

    # TODO: is return True 'pythonic', something better?
    return True


# user functions
def post_collection(session, **kwarg):
    """Posts collection to the database
    Return: collection; 'newly posted collection'
    """
    payload = {}
    data = {}

    # build POST data payload query from user data, **kwarg
    for k, v in kwarg.items():
        payload[k] = v[0]

    # validate payload agaisnt database columnns, automate None to empty fields
    for column in Collection.__table__.columns:
        if column.name in payload:
            data[column.name] = payload[column.name]
        elif column.name not in payload:
            data[column.name] = None
        else:
            pass

    # init collection object
    collection = Collection(
        name=data['name'], image=data['image'], author=data['author']
    )

    # append default cover to Collection object, if 'None'
    # TODO: can possibly do this during validation?
    if data['image_thumb'] == None:
        collection.image_thumb = 'default_cover.jpg'
    else:
        collection.image_thumb = data['image_thumb']

    # commit new collection.
    session.add(collection)
    session.commit()

    return collection


def post_asset(session, **kwarg):
    """Posts asset to the database
    Return: asset; 'new posted aset'
    """
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

    # I think i put this here because the asset had to be 'init' with
    # session.add() because i needed to append new tags?
    # TODO: understand before better, refactor multiple session hits might not
    # be needed?
    session.add(asset)

    if 'tags' in payload:
        tags = payload['tags'].split()
        for term in tags:
            newtag = Tag(name=term)
            asset.tags.append(newtag)

    # commit changes to database
    session.commit()

    return asset


def get_collections(session):
    """Returns list of dict collection objects"""
    # querys for all Collection objects in order of id, appends to list
    # TODO: This should return objects in order of moddate
    collections = []
    for collection in session.query(Collection).order_by(Collection.id):
        collections.append(collection)

    # iterates through 'collections' objects to build dicts of objects, 'item'
    result = []
    for collection in collections:
        item = {}
        for column in collection.__table__.columns:
            item[column.name] = str(getattr(collection, column.name))

        # Additional many-to-many data
        # init tags
        # TODO: remove try/except
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

        # TODO: '.append(str(assignment))' needd to append a dict of data.
        for assignment in assignments:
            item['assets'].append(str(assignment))

        # appends final 'item' rep of collection object.
        result.append(item)

    # returns list of dicts, collection assets
    return result


def get_assets(session):
    """Returns all asset objects"""
    # querys for all asset objects in order of moddate, appends to list
    assets = []
    for asset in session.query(Asset).order_by(Asset.moddate):
        assets.append(asset)

    # iterates through 'assets' objects to build dicts of objects, 'item'
    result = []
    for asset in assets:
        item = {}
        for column in asset.__table__.columns:
            item[column.name] = str(getattr(asset, column.name))

        # Additional many-to-many data
        # init collections
        # TODO: look inot '.first()' is this the quickest way to return a unique
        # result?
        item['collections'] = []
        # get assets collections via many-to-many
        assets_collections = session.query(Asset).filter_by(
            id=asset.id
        ).first().collections

        # append object data to 'item'.
        # TODO: '.append(str(collection))' needs to be a dict of the collections
        # data.
        for collection in assets_collections:
            item['collections'].append(str(collection))

        # init tags
        # TODO: Needs to impltement 'set{}' for duplicate tags?
        item['tags'] = []
        for tag in asset.tags:
            item['tags'].append(tag.name)

        # append 'item' of asset object
        result.append(item)

    # returns list of dict,
    return result


def get_asset_by_id(session, id):
    """Return asset object as a dict using Asset.id"""
    # querys for asset object
    asset_by_id = session.query(Asset).get(id)

    # if asset is found, build dict of object, 'item'
    if asset_by_id:
        item = {}

        for column in asset_by_id.__table__.columns:
            item[column.name] = str(getattr(asset_by_id, column.name))

        # Additional many-to-many data

        # init tags
        # TODO: '.append(str(tag.name))' could more info be used here? like
        # {'name': 'int(assets rate?)'} maybe too advanced?
        item['tags'] = []
        assets_tags = session.query(Asset).filter_by(id=asset_by_id.id).first().tags

        for tag in assets_tags:
            item['tags'].append(str(tag.name))

        # init collections
        # TODO: '.append(str(collection))' will need to be dict of collection
        # object
        item['collections'] = []
        # get assets collections via many-to-many
        assets_collections = session.query(Asset).filter_by(id=asset_by_id.id).first().collections

        # append collection objects to 'item'
        for collection in assets_collections:
            item['collections'].append(str(collection))

    else:
        # TODO: Is this needed?
        item = {}

    # returns dic, 'item' repr of asset object
    return item


def get_collection_by_id(session, id):
    """Returns collection object as dict using Collection.id"""
    # querys for collection object
    collection_by_id = session.query(Collection).get(id)

    # if collection exists, build dict from data, 'item'
    if collection_by_id:
        result = {}

        for column in collection_by_id.__table__.columns:
            result[column.name] = str(getattr(collection_by_id, column.name))

        # Additional many-to-mnay data
        # init tags
        # TODO: '.append(str(tag.name))' could more info be used here? like
        # {'name': 'int(assets rate?)'} maybe too advanced?
        result['tags'] = []
        collections_tags = collection_by_id.tags

        for tag in collections_tags:
            result['tags'].append(str(tag.name))

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


# TODO: Can all these get_query_* re refactored to a single methods? using
# flags or something.
def get_query(session, userquery):
    """takes list of words and returns related objects"""
    # TODO: DEV: needs to be rewritten to account for many-to-many relationships
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
    # TODO: DEV: rewritten to account for many-to-many relationships.
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
    """query tags"""
    # TODO: DEV: rewritten to account for many-to-many relationships.
    # What is this?

    # bla = session.query(Asset).filter(Asset.tag).all()
    #hrr = session.query(Asset).order_by(Asset.id)

    return False


def patch_assety(session, **user_columns):
    """updates asset fields using user data"""
    # TODO: earlist issues meant the function had 'y' added to the end. clean up
    # function name
    # TODO: This is a pretty heftly function... needs refactoring

    # init query dict
    query = {}
    # asset id
    id = int(user_columns['id'])

    # build list of assets column names for validation
    asset_columns = Asset.__table__.columns.keys()

    # validate user data and build query dict, from data.
    for k, v in user_columns.items():
        if k in asset_columns:
            query[k] = v

        else:
            pass

        # additional many-to-many data
        if k == 'collections':
            query[k] = v.split()

        elif k == 'tags':
            query['tags'] = v.split()

        else:
            pass

    # once all user data is validated and ready to append, get asset object.
    asset = session.query(Asset).get(id)

    # Process user data and update asset object fields.
    # TODO: is there a better way to handle these sort of 'flags'?
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
            # process asset tags
            for tag in v:
                # create new Tag object and append to asset object
                # TODO: Could this be a point to implement a 'set{}' for
                # duplicutes
                newtag = Tag(name=str(tag))
                session.add(newtag)

                asset.tags.append(newtag)

        elif k == 'flag':
            # process flag field
            # if 'flag' is true value is increased
            if int(query['flag']) == 1:
                # TODO: is a try/except needed here?
                try:
                    asset.flag += 1

                except TypeError:
                    asset.flag = 0
                    asset.flag += 1

            # if 'flag' is false value is reduced
            elif int(query['flag']) == 0:
                asset.flag -= 1

            # is the 'else:' 'pythonic'?
            else:
                pass

        elif k == 'collections':
            for collection_id in query['collections']:
                # get Collection object using collection.id
                existingcollection = session.query(Collection).get(collection_id)
                # append existing collection to assets collections
                asset.collections.append(existingcollection)

        else:
            pass

    # Finish asset object
    # append object moddate
    asset.moddate = datetime.datetime.utcnow()

    session.add(asset)
    session.commit()

    # Returns asset object
    return asset


def patch_collectiony(session, id, **user_columns):
    """updates users defined columns with user defined values"""
    # TODO: earlist issues meant the function had 'y' added to the end. clean up
    # function name
    # TODO: This is a pretty heftly function... needs refactoring
    # init query dict

    #init query dict
    query = {}

    # build list of collections columnnams for validation
    collection_columns = Collection.__table__.columns.keys()

    # validdate uer data and build query dict, from data.
    for k, v in user_columns.items():
        if k in collection_columns:
            query[k] = v

        else:
            pass

        # additional many-to-many data
        if k == 'assets':
            query[k] = v.split()

        elif k == 'tags':
            query[k] = v.split()

        elif k == 'remove_assets':
            query[k] = v.split()

        else:
            pass

    # once all user data is alidate and ready to append, get collection object
    collection = session.query(Collection).get(id)

    # process user data and update collection object fields.
    # TODO: is there a better way to handle these sort of 'flags'?
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
                try:
                    # get asset object and append to collection
                    newasset = session.query(Asset).get(int(asset_id))
                    collection.assets.append(newasset)

                except:
                    pass

        elif k == 'remove_assets':
            for asset_id in v:
                # TODO: dont use try/except for this
                try:
                    # get asset object and remove from collection.
                    # TODO: is there a quicker way? without getting the object first?
                    removeasset = session.query(Asset).get(int(asset_id))
                    collection.assets.remove(removeasset)

                except:
                    pass

        elif k == 'tags':
            for x in v:
                # create to Tag objects and append to collection.
                # TODO: Could this be a point to implement a 'set{}' for
                # duplicutes
                newtag = Tag(name=str(x))
                session.add(newtag)

                collection.tags.append(newtag)

        elif k == 'flag':
            # process flag field
            # if 'flag' is true value is increased
            if int(query['flag']) == 1:
                # TODO: is a try/except needed here?
                try:
                    collection.flag += 1

                except TypeError:
                    collection.flag = 0
                    collection.flag += 1

            # if 'flag' is false value is reduced
            elif int(query['flag']) == 0:
                collection.flag -= 1

            # is the 'else:' 'pythonic'?
            else:
                pass
        else:
            pass

    # Finish asset object
    # append object moddate
    collection.moddate = datetime.datetime.utcnow()

    session.add(collection)
    session.commit()

    # Returns asset object
    return collection


def delete_assety(session, asset_id):
    """deletes asset object"""
    # TODO: DEV: rewritten to account for many-to-many relationships.
    session.query(Asset).filter(Asset.id=='{}'.format(asset_id)).delete()
    session.commit()

    return False


def delete_collectiony(session, collection_id):
    """deletes collection object"""
    # TODO: DEV: rewritten to account for many-to-many relationships.
    print('whaaa')

    # myparent.children.remove(somechild)

    # session.query(Collection).filter(Collection.id=='{}'.format(collection_id)).delete()
    # session.commit()``

    return False
