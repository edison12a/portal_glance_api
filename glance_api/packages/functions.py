"""
This module contains functions for ...
"""

__author__ = ""
__version__ = ""
__license__ = ""

# TODO: classes needed?
import datetime
from .models import Collection, Base, Footage, User, Item, Image, Geometry, Collection, Tag, tag_ass, People


# dev functions
def __reset_db(session, engine):
    """DEV: drops tables and rebuild"""
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
        Base.metadata.create_all(engine)
    except:
        print('---------------------------')
        print('Tables have not been built.')
        print('---------------------------')

    print('----------------------------------------')
    print('Tables removed, and re-built successful.')
    print('----------------------------------------')

    # TODO: is return True 'pythonic', something better?
    return True


# helper functions
def to_dict(item_list):
    """ takes list of database objects, returns dict repr of objects. """
    # TODO: using '__tablename__' on objects does the same jobs as 'item_type'
    # any point in having it as column?
    result = []
    # check if `item_list` is iterable
    if isinstance(item_list, list) or isinstance(item_list, tuple):
        pass
    else:
        item_list = (item_list,)

    # remove duplicate results
    item_list = list(set(item_list))

    # for each database object, build dict, 'item', from data.
    for item_object in item_list:
        item = {}
        for column in item_object.__table__.columns:
            item[column.name] = str(getattr(item_object, column.name))

        # init tags
        item['tags'] = []
        assets_tags = item_object.tags

        for tag in assets_tags:
            item['tags'].append(str(tag.name))

        # init collections
        if item_object.item_type == 'collection':

            item['items'] = {}
            for x in item_object.items:
                item['items'][x.id] = {
                    'id': x.id,
                    'item_thumb': x.item_thumb,
                    'item_type': x.item_type
                }

        else:
            item['collections'] = {}
            for x in item_object.collections:
                item['collections'][x.id] = {
                    'id': x.id,
                    'item_thumb': x.item_thumb,
                    'name': x.name
                }

        result.append(item)

    # return database objects as dicts.
    return result


# query
# TODO: Can all these get_query_* re refactored to a single methods? using
# flags or something.
def get_tag(session, data):
    if data == None:
        result = [str(x.name) for x in session.query(Tag).all()]
        return result
    else:
        # TODO: IF data == 'id' return that ids tags.
        return False

    return Fales


def get_items(session, filter='all'):
    """Returns all asset objects"""
    # TODO: IMP filtering
    raw_items = session.query(Item).all()

    if filter == 'all':
        result = to_dict([x for x in raw_items])
    else:
        result = to_dict([x for x in raw_items if x.item_type == filter])

    # returns raw db objects
    return result


def get_item_by_id(session, id):
    """Return asset object as a dict using Asset.id"""
    # querys for asset object
    asset_by_id = session.query(Item).get(id)

    # returns raw asset
    return asset_by_id


def get_collection_by_author(session, author):
    collection_by_author = session.query(Collection).filter_by(author=author).all()
    return collection_by_author


def get_query(session, userquery):
    """takes list of words and returns related objects"""
    # TODO: currently searching every table with every query term, multiple
    # searches. gotta be a better way. look into postgres joins?
    result = {}
    query = {}

    # makes users query a dict
    for k, v in userquery.items():
        query[k] = str(v).split()

    if 'filter' not in query:
        query['filter'] = 'all'
    else:
        query['filter'] = query['filter'][0]

    # querying through many-to-many relationships leaves us with an
    # instrumentedlist which needs to be exracted before using make_dict
    item_list = []
    for term in query['query']:
        # return list of tags
        if term == '**':
            # TODO: This is suuuuper slow. query item table directly.
            taglists = session.query(Tag).all()
        else:
            taglists = session.query(Tag).filter_by(name=term).all()

        # for each tag
        for tag in taglists:
            # if one exists
            if tag.items:
                # get asset assigned to tag and append to list, 'item_list'
                for item in tag.items:
                    # return data according to the filter information
                    if query['filter'] == 'all':
                        item_list.append(item)
                    else:
                        if item.item_type == query['filter']:
                            item_list.append(item)
                        else:
                            pass
            # get collection assigned to tag and append to list, 'item_list'
            elif tag.collection_tags:
                for item in tag.collection_tags:
                    item_list.append(item)

    return item_list


def get_user(session, **kwarg):

    # TODO: if test == NONETYPE, return False

    test = session.query(User).filter_by(username=kwarg['username']).first()

    if test is not None and test.password == kwarg['password']:
        result = True
    else:
        result = False

    # returns raw db objects
    return result


# crud
def post_asset(session, **kwarg):
    """Posts asset to the database
    Return: asset; 'new posted aset'
    """

    payload = {}
    data = {}

    # process user input
    for k, v in kwarg.items():
        if k == 'tag':
            bla = v.split(' ')
            payload[k] = bla
        else:
            payload[k] = v

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
    # TODO: understand before better, refactor, multiple session hits might not
    # be needed?
    session.add(asset)

    if 'tag' in payload:
        for tag in payload['tag']:
            newtag = Tag(name=str(tag))
            session.add(newtag)
            asset.tags.append(newtag)

    # commit changes to database
    session.commit()

    return asset


def patch_item_by_id(session, **user_columns):
    """updates asset fields using user data"""
    # TODO: This is a pretty heftly function... needs refactoring

    # init query dict
    query = {}

    # asset id
    id = int(user_columns['id'])

    # build list of assets column names for validation
    # asset_columns = Item.__table__.columns.keys()
    # print(asset_columns)

    # validate user data and build query dict, from data.
    for k, v in user_columns.items():
        # additional many-to-many data
        if k == 'collections':
            query[k] = v.split()
        elif k == 'items':
            query[k] = v.split()

        elif k == 'tags':
            query['tags'] = v.split()

        else:
            query[k] = v

    # once all user data is validated and ready to append, get asset object.
    asset = session.query(Item).get(id)

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

        elif k == 'items':
            # process asset tags
            for item in v:
                item_to_collection = session.query(Item).get(int(item))
                asset.items.append(item_to_collection)
                session.add(asset)

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

    result = to_dict((asset,))

    # Returns asset object
    return result


def del_item(session, id):
    """deletes item object"""
    # TODO: also delete physical files.
    # delete add item to session for deletion
    item = session.query(Item).filter_by(id='{}'.format(int(id))).first()
    session.delete(item)
    session.commit()
    # check if any assciations remain on `Tag` if None then delete it.
    # TODO: this should problely be handled by something else tag related?
    for x in item.tags:
        if len(x.items) > 0:
            pass
        else:
            # delete the tag
            print('deleting {}'.format(x))
            session.delete(x)

    session.commit()

    return True


def post_user(session, **kwarg):
    data = {}

    # process user input
    for k, v in kwarg.items():
        data[k] = v

    # Database entry
    user = User(
        username=data['username'], password=data['password']
    )

    session.add(user)
    session.commit()

    return user


def post_image(session, **kwarg):
    payload = {}
    data = {}
    tag_ids = []

    # process user input
    for k, v in kwarg.items():
        payload[k] = v

    # remove attri that arnt in the database
    for column in Image.__table__.columns:
        if column.name in payload:
            data[column.name] = payload[column.name]
        elif column.name not in payload:
            data[column.name] = None
        else:
            pass

    print(data)
    # Database entry
    item = Image(
        name = data['name'],
        item_loc = data['item_loc'],
        item_thumb = data['item_thumb'],
        author = data['author'],
        attached = data['attached']
    )

    session.add(item)
    session.commit()

    # after entry is commited then hit the database with any new tags?
    # is this the best way?
    if 'tags' in payload:
        tag_list = payload['tags'].split(' ')
        for tag in tag_list:

            # TODO: refactor the below its checking to see if the tags exists already
            #if it does then just append that tag with the item object.
            #else make a new tag object
            test = session.query(Tag).filter_by(name=tag).first()

            if test:
                test.items.append(item)
                session.add(test)
                session.commit()
            else:
                newtag = Tag(name=str(tag))
                session.add(newtag)
                session.commit()

                item.tags.append(newtag)

    session.add(item)
    # commit changes to database
    session.commit()

    return item


def post_footage(session, **kwarg):
        payload = {}
        data = {}

        # process user input
        for k, v in kwarg.items():
            payload[k] = v

        # remove attri that arnt in the database
        for column in Image.__table__.columns:
            if column.name in payload:
                data[column.name] = payload[column.name]
            elif column.name not in payload:
                data[column.name] = None
            else:
                pass

        # Database entry
        item = Footage(
            name = data['name'],
            item_loc = data['item_loc'],
            item_thumb = data['item_thumb'],
            author = data['author'],
            attached = data['attached']
        )

        # after entry is commited then hit the database with any new tags?
        if 'tags' in payload:
            tag_list = payload['tags'].split(' ')
            for tag in tag_list:

                # is this the best way?
                # TODO: refactor the below its checking to see if the tags exists already
                #if it does then just append that tag with the item object.
                #else make a new tag object
                test = session.query(Tag).filter_by(name=tag).first()

                if test:
                    test.items.append(item)
                    session.add(test)
                    session.commit()
                else:
                    newtag = Tag(name=str(tag))
                    session.add(newtag)
                    session.commit()

                    item.tags.append(newtag)


        # TODO: sort out tags
        session.add(item)
        # commit changes to database
        session.commit()

        return item


def post_geometry(session, **kwarg):
    payload = {}
    data = {}

    # process user input
    for k, v in kwarg.items():
        payload[k] = v

    # remove attri that arnt in the database
    for column in Geometry.__table__.columns:
        if column.name in payload:
            data[column.name] = payload[column.name]
        elif column.name not in payload:
            data[column.name] = None
        else:
            pass

    # Database entry
    item = Geometry(
        name = data['name'],
        item_loc = data['item_loc'],
        item_thumb = data['item_thumb'],
        author = data['author'],
        attached = data['attached']
    )

    # after entry is commited then hit the database with any new tags?
    # is this the best way?
    if 'tags' in payload:
        tag_list = payload['tags'].split(' ')
        for tag in tag_list:

            # TODO: refactor the below its checking to see if the tags exists already
            #if it does then just append that tag with the item object.
            #else make a new tag object
            test = session.query(Tag).filter_by(name=tag).first()

            if test:
                test.items.append(item)
                session.add(test)
                session.commit()
            else:
                newtag = Tag(name=str(tag))
                session.add(newtag)
                session.commit()

                item.tags.append(newtag)


    # TODO: sort out tags
    session.add(item)
    # commit changes to database
    session.commit()

    return item


def post_people(session, **kwarg):
    payload = {}
    data = {}

    # process user input
    for k, v in kwarg.items():
        payload[k] = v


    # remove attri that arnt in the database
    for column in People.__table__.columns:
        if column.name in payload:
            data[column.name] = payload[column.name]
        elif column.name not in payload:
            data[column.name] = None
        else:
            pass

    # Database entry
    item = People(
        name = data['name'],
        item_loc = data['item_loc'],
        item_thumb = data['item_thumb'],
        author = data['author'],
        # attached = data['attached']
    )
    session.add(item)
    session.commit()


    print('dsfsssssssssssssssssssssssssssssssssssssssssssss')
    print('its people bab!')

    print(item.name)

    # after entry is commited then hit the database with any new tags?
    # is this the best way?
    if 'tags' in payload:
        tag_list = payload['tags'].split(' ')
        for tag in tag_list:

            # TODO: refactor the below its checking to see if the tags exists already
            #if it does then just append that tag with the item object.
            #else make a new tag object
            test = session.query(Tag).filter_by(name=tag).first()

            if test:
                test.items.append(item)
                session.add(test)
                session.commit()
            else:
                newtag = Tag(name=str(tag))
                session.add(newtag)
                session.commit()

                item.tags.append(newtag)


    # TODO: sort out tags
    session.add(item)
    # commit changes to database
    session.commit()

    return item


def post_collection(session, **kwarg):
    print('AM I HERE?!?!?!')
    payload = {}
    data = {}

    # process user input
    for k, v in kwarg.items():
        payload[k] = v

    # remove attri that arnt in the database
    for column in Collection.__table__.columns:
        if column.name in payload:
            data[column.name] = payload[column.name]
        elif column.name not in payload:
            data[column.name] = None
        else:
            pass

    # Database entry
    item = Collection(
        name = data['name'],
        item_loc = data['item_loc'],
        item_thumb = data['item_thumb'],
        author = data['author']

    )

    # after entry is commited then hit the database with any new tags?
    # is this the best way?
    if 'tags' in payload:
        tag_list = payload['tags'].split(' ')
        for tag in tag_list:

            # TODO: refactor the below its checking to see if the tags exists already
            #if it does then just append that tag with the item object.
            #else make a new tag object
            test = session.query(Tag).filter_by(name=tag).first()

            if test:
                test.items.append(item)
                session.add(test)
                session.commit()
            else:
                newtag = Tag(name=str(tag))
                session.add(newtag)
                session.commit()

                item.tags.append(newtag)
    else:
        payload['tags'] = ''

    print('PAYLOADPAYLOADPAYLOAD')
    print(payload)
    print(payload['items'])

    if 'items' in payload:

        collection = session.query(Collection).get(item.id)

        for item_id in payload['items'].split(' '):
            item_to_append = session.query(Item).get(int(item_id))
            collection.items.append(item_to_append)
            session.add(collection)
            session.commit()

    else:
        payload['items'] = ''

    # TODO: sort out tags
    session.add(item)
    # commit changes to database
    session.commit()

    return item
