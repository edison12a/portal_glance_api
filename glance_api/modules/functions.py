"""
This module contains Classes and helpers for the API
"""

__author__ = ""
__version__ = ""
__license__ = ""

import datetime

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


# helper functions
def to_dict(item_list):
    """Converts database object to dict.

    :param item_list: Tuple, `glance_api.modules.models.Item`

    :return: dict repr of database object.
    :return type: Tuple. 'glance_api.modules.models.Item'
    """

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


# auth
# TODO: Refactor to User() class
def get_user(session, **kwarg):
    """Checks database to see if users credentials are correct.

    :param session: 'sqlalchemy.orm.session.Session'.
    :param kwarg:
    :param username: str.
    :param password: str.

    :return type: bool
    """
    # TODO: consider renaming, `check_user` or something.
    # TODO: if test == NONETYPE, return False

    test = session.query(glance_api.modules.models.User).filter_by(username=kwarg['username']).first()

    if test is not None and test.password == kwarg['password']:
        result = True
    else:
        result = False

    return result


def post_user(session, **kwarg):
    """Creates a new user

    :param session: 'sqlalchemy.orm.session.Session'.
    :param kwarg:
    :param username: str.
    :param password: str.

    :return: user object
    :return type: database object.
    """

    data = {}

    # process user input
    for k, v in kwarg.items():
        data[k] = v

    # Database entry
    user = glance_api.modules.models.User(
        username=data['username'], password=data['password']
    )

    session.add(user)
    session.commit()

    return user


# query
# TODO: refactor to Query() class
def get_tag(session, data):
    """Retrive Tag objects from database.

    :param session: 'sqlalchemy.orm.session.Session'.
    :param data: sqlalchemy objects.

    :return: List
    """
    if data == None:
        result = [str(x.name) for x in session.query(glance_api.modules.models.Tag).all()]
        return result
    else:
        # TODO: IF data == 'id' return that ids tags.
        return False

    return False


def get_collection_by_author(session, author):
    """Get authors collections.

    Keyword arguments:
    session -- Sqlalchemy session object.
    author -- STRING. Author name.

    Return:
    List of database objects.
    """
    # TODO: new docstrings
    collection_by_author = session.query(glance_api.modules.models.Collection).filter_by(author=author).all()
    return collection_by_author


def get_query(session, userquery):
    """Get database objects based user term.

    Keyword arguments:
    session -- Sqlalchemy session object.
    userquery -- str.

    Return: List
    """
    # TODO: new docstrings
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
            taglists = session.query(glance_api.modules.models.Tag).all()
        else:
            taglists = session.query(glance_api.modules.models.Tag).filter_by(name=term).all()

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


# crud
# TODO: refactor to Item() class
def post_collection(session, **kwarg):
    """Add new collection Item to database.

    Keyword arguments:
    session -- Sqlalchemy session object.
    kwarg -- ???

    Return: Item
    """
    payload = {}
    data = {}

    # process user input
    for k, v in kwarg.items():
        payload[k] = v

    # remove attri that arnt in the database
    for column in glance_api.modules.models.Collection.__table__.columns:
        if column.name in payload:
            data[column.name] = payload[column.name]
        elif column.name not in payload:
            data[column.name] = None
        else:
            pass

    # Database entry
    item = glance_api.modules.models.Collection(
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
            test = session.query(glance_api.modules.models.Tag).filter_by(name=tag).first()

            if test:
                test.items.append(item)
                session.add(test)
                session.commit()
            else:
                newtag = glance_api.modules.models.Tag(name=str(tag))
                session.add(newtag)
                session.commit()

                item.tags.append(newtag)
    else:
        payload['tags'] = ''

    if 'items' in payload:

        collection = session.query(glance_api.modules.models.Collection).get(item.id)

        for item_id in payload['items'].split(' '):
            item_to_append = session.query(glance_api.modules.models.Item).get(int(item_id))
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


## oop
class Item():
    """Constructs a generic :class:`Item`"""
    def __init__(self, session):
        self.session = session

    def get(self, id=None, filter=None):
        """get item.

        id: primary key of database item, `None` returns all
        filter: item_type of database item, limit results to item_type
        """
        # TODO: imp control flow
        if id == None:
            if filter == None or filter == 'all':
                items = self.session.query(glance_api.modules.models.Item).all()
                return items
            else:
                items = self.session.query(glance_api.modules.models.Item).filter(glance_api.modules.models.Item.type==filter).all()
                return items

        else:
            item = self.session.query(glance_api.modules.models.Item).get(id)
            return item

    def delete(self, id):
        """ deletes item from database.

        id: primary key of database item,
        """
        item = self.session.query(glance_api.modules.models.Item).filter_by(id='{}'.format(int(id))).first()
        self.session.delete(item)
        self.session.commit()

        # check if any assciations remain on `Tag` if None then delete it.
        # TODO: this should problely be handled by something else tag related?
        for x in item.tags:
            if len(x.items) > 0:
                pass
            else:
                # delete the tag
                print('deleting {}'.format(x))
                self.session.delete(x)

        self.session.commit()

        return True

    # item type posts
    # TODO: collections, tags
    def post(self, kwarg):
        """post item to database.

        kwarg: dict. user data to process.
        return: new `Item` object
        """
        # TODO: make item_types global?
        # TODO: tags
        item_types = {
            'image': glance_api.modules.models.Image,
            'footage': glance_api.modules.models.Footage,
            'geometry': glance_api.modules.models.Geometry,
            'people': glance_api.modules.models.People,
            'collection': glance_api.modules.models.Collection
            }

        # process universal data
        # structures
        payload = {}
        data = {}

        # process user input
        for k, v in kwarg.items():
            payload[k] = v

        # process user data
        for column in item_types[payload['item_type']].__table__.columns:
            if column.name in payload:
                data[column.name] = payload[column.name]
            elif column.name not in payload:
                data[column.name] = None
            else:
                pass

        item = item_types[payload['item_type']](
            name = data['name'],
            item_loc = data['item_loc'],
            item_thumb = data['item_thumb'],
            author = data['author'],
            attached = data['attached']
        )

        if payload['item_type'] == 'collection':
            for x in payload['items'].split(' '):
                item.items.append(self.session.query(glance_api.modules.models.Item).get(x))

        self.session.add(item)
        self.session.commit()


        # prepare tags for item

        # after entry is commited then hit the database with any new tags?
        # is this the best way?
        if 'tags' in payload:
            tag_list = payload['tags'].split(' ')
            for tag in tag_list:

                # TODO: refactor the below its checking to see if the tags exists already
                #if it does then just append that tag with the item object.
                #else make a new tag object
                test = self.session.query(glance_api.modules.models.Tag).filter_by(name=tag).first()

                if test:
                    test.items.append(item)
                    self.session.add(test)
                    self.session.commit()
                else:
                    newtag = glance_api.modules.models.Tag(name=str(tag))
                    self.session.add(newtag)
                    self.session.commit()

                    item.tags.append(newtag)

        self.session.add(item)
        # commit changes to database
        self.session.commit()

        return item


    def patch(self, kwarg):
        """updates asset fields using user data"""
        # TODO: This is a pretty heftly function... needs refactoring

        # init query dict
        query = {}
        query['tags'] = []

        # asset id
        id = int(kwarg['id'])

        # build list of assets column names for validation

        # validate user data and build query dict, from data.
        for k, v in kwarg.items():
            # additional many-to-many data
            if k == 'collections':
                query[k] = v.split()
            elif k == 'items':
                query[k] = v.split()
            elif k == 'tags':
                query['tags'] = v.split()
            elif k == 'people_tags':
                # get items current tags
                current_tags = to_dict((self.session.query(glance_api.modules.models.Item).get(kwarg['id']),))[0]['tags']
                # append new tags only if they arent in current_tags
                for x in kwarg[k].split(' '):
                    if x not in current_tags:
                        query['tags'].append(x)
                    else:
                        pass
            else:
                query[k] = v


        # once all user data is validated and ready to append, get asset object.
        asset = self.session.query(glance_api.modules.models.Item).get(id)
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
                # remove dups
                tag_list = list(set(v))

                for tag in tag_list:
                    # create new Tag object and append to asset object
                    newtag = glance_api.modules.models.Tag(name=str(tag))
                    self.session.add(newtag)

                    asset.tags.append(newtag)

            elif k == 'items':
                # process asset tags
                for item in v:
                    item_to_collection = self.session.query(glance_api.modules.models.Item).get(int(item))
                    asset.items.append(item_to_collection)
                    self.session.add(asset)

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
                    existingcollection = self.session.query(glance_api.modules.models.Collection).get(collection_id)
                    # append existing collection to assets collections
                    asset.collections.append(existingcollection)

            else:
                pass

        # Finish asset object
        # append object moddate
        asset.moddate = datetime.datetime.utcnow()

        self.session.add(asset)
        self.session.commit()

        # Returns asset object
        return asset


    def __repr__(self):
        return '<Item>'
