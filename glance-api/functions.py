# TODO: classes needed?
import datetime
from models import assignment, tag_table, Collection, Tag, Asset


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

# helper functions
def make_dict(item_list):
    """ takes list of database objects, returns dict repr of objects. """
    # TODO: using '__tablename__' on objects does the same jobs as 'item_type'
    # any point in having it as column?
    result = []

    # for each database object, build dict, 'item', from data.
    for item_object in item_list:
        item = {}
        for column in item_object.__table__.columns:
            item[column.name] = str(getattr(item_object, column.name))

        # additional many-to-many data
        # init tags
        # TODO: '.append(str(tag.name))' could more info be used here? like
        # {'name': 'int(assets rate?)'} maybe too advanced?
        if item_object.item_type == 'asset':
            # If object is asset
            # init tags
            item['tags'] = []
            assets_tags = item_object.tags

            for tag in assets_tags:
                item['tags'].append(str(tag.name))

            # init collections
            item['collections'] = []
            # get assets collections via many-to-many
            assets_collections = item_object.collections

            # append collection objects to 'item'
            for collection in assets_collections:
                item['collections'].append(str(collection))

        elif item_object.item_type == 'collection':
            # If object is a collection
            # init tags
            item['tags'] = []
            collections_tags = item_object.tags

            for tag in collections_tags:
                item['tags'].append(str(tag.name))

            # init assets
            item['assets'] = []
            assignments = item_object.assets

            for assignment in assignments:
                item['assets'].append(str(assignment))

        result.append(item)

    # return database objects as dicts.
    return result

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
    result = make_dict(collections)

    # returns list of dicts, collection assets
    return result


def get_assets(session):
    """Returns all asset objects"""
    # querys for all asset objects in order of moddate, appends to list
    assets = []
    for asset in session.query(Asset).order_by(Asset.moddate):
        assets.append(asset)

    # iterates through 'assets' objects to build dicts of objects, 'item'
    result = make_dict(assets)

    # returns list of dict,
    return result


def get_asset_by_id(session, id):
    """Return asset object as a dict using Asset.id"""
    # querys for asset object
    asset_by_id = session.query(Asset).get(id)

    # if asset is found, build dict of object, 'item'
    if asset_by_id:
        item = make_dict((asset_by_id,))

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
        result = make_dict((collection_by_id,))

    else:
        result = {}

    return result


# TODO: Can all these get_query_* re refactored to a single methods? using
# flags or something.
def get_query(session, userquery):
    """takes list of words and returns related objects"""
    # TODO: currently searching every table with every query term, multiple
    # searches. gotta be a better way. look into postgres joins?
    result = {}

    # makes users query a dict
    for k, v in userquery.items():
        query = {k: str(v).split()}

    # querying through many-to-many relationships leaves us with an
    # instrumentedlist which needs to be exracted before using make_dict
    item_list = []
    for term in query['query']:
        # return list of tags
        taglists = session.query(Tag).filter_by(name=term).all()
        # for each tag
        for tag in taglists:
            # if one exists
            if tag.item:
                # get asset assigned to tag and append to list, 'item_list'
                for item in tag.item:
                    item_list.append(item)
            # get collection assigned to tag and append to list, 'item_list'
            elif tag.collection_tags:
                for item in tag.collection_tags:
                    item_list.append(item)

    # run items through make_dict for the return
    result = make_dict(item_list)

    return result


def get_query_flag(session, flag):
    """ Returns list of flagged items """
    # TODO: DEV: rewritten to account for many-to-many relationships.
    assets = []
    for item in session.query(Asset).filter(Asset.flag>=1).order_by(Asset.id):
        assets.append(item)

    for item in session.query(Collection).filter(Collection.flag>=1).order_by(Collection.id):
        assets.append(item)

    result = []
    for asset in assets:
        item = make_dict(asset)
        result.append(item)

    return result


def patch_asset(session, **user_columns):
    """updates asset fields using user data"""
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

    result = make_dict((asset,))

    # Returns asset object
    return result


def patch_collection(session, id, **user_columns):
    """updates users defined columns with user defined values"""
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

    result = make_dict((collection,))

    # Returns collection object
    return result


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