"""
This module contains Classes and helpers for the API
"""

import datetime

from sqlalchemy.inspection import inspect
import sqlalchemy.orm

import glance_api.modules.models


def jsonify(query):
    result = []

    for row in query:
        to_append = {}

        # get object columns and data
        for column in row.__table__.columns:
            column_header = str(column).split('.')[1]
            to_append[column_header] = str(getattr(row, column_header))

        # get objects relationship columns and data
        inspect_row = inspect(row).__dict__['class_'].__dict__.keys()

        for column_name in inspect_row:
            if not column_name.startswith('_'):
                if column_name not in row.__table__.columns:
                    if column_name != 'type' and '_sa_adapter' in getattr(row, column_name).__dict__.keys():
                        # 'sqlalchemy.orm.collections.InstrumentedList'
                        item_collect = []

                        for relationship_row in getattr(row, column_name):
                            item = {}
                            for data in relationship_row.__table__.columns:
                                item[str(data).split('.')[1]] = str(getattr(relationship_row, str(data).split('.')[1]))

                            item_collect.append(item)

                        to_append[column_name] = item_collect

                    else:
                        # 'sqlalchemy.orm.dynamic.AppenderBaseQuery'
                        item_collect = []

                        for relationship_row in getattr(row, column_name):
                            if not isinstance(relationship_row, str):
                                for data in relationship_row.__table__.columns:
                                    item[str(data).split('.')[1]] = getattr(relationship_row, str(data).split('.')[1])

                                item_collect.append(item)

                        to_append[column_name] = item_collect

        result.append(to_append)

    return result


def get_account(session, **kwarg):
    """Checks database to see if users credentials are correct.

    :param session: 'sqlalchemy.orm.session.Session'.
    :param kwarg:
    :param username: str.
    :param password: str.

    :return type: bool
    """
    # TODO: consider renaming, `check_user` or something.
    # TODO: if test == NONETYPE, return False

    test = session.query(glance_api.modules.models.Account).filter_by(username=kwarg['username']).first()

    if test is not None and test.password == kwarg['password']:
        result = True
    else:
        result = False

    return result


# user query start
def construct_query_dict(userquery):
    data = dict(userquery)
    query = {}

    # init query object
    if 'filter' not in data:
        query['filter'] = 'all'
    else:
        query['filter'] = data['filter']


    if 'filter_people' not in data or data['filter_people'] == None:
        query['filter_people'] = None
    else:
        query['filter_people'] = data['filter_people']

    filter_people = []
    if 'filter_people' in data:
        filter_people = data['filter_people']

    # construct query
    query = {
        'filter': data['filter'],
        'filter_people': filter_people,
        'query': data['query']
    }

    return query


def get_tags_from_query(session, query):
    tags = []
    # filter items with [query]
    if query['query'] == '**' or query['query'] == '':
        tags = [x for x in session.query(glance_api.modules.models.Tag).all()]

    else:
        for tag in query['query'].split(' '):
            raw_tags = [x for x in session.query(glance_api.modules.models.Tag).filter_by(name=tag).all()]

        # TODO: Start to implement pagination, and sorted search results.
        for x in query['query'].split(' '):
            raw_tags = [x for x in session.query(glance_api.modules.models.Tag).filter_by(name=x).limit(100)]

            for tag in raw_tags:
                tags.append(tag)

    return tags


def filter_tags(query, tags):
    items = []
    # further filter items with [filter]
    for tag in tags:
        for item in tag.items:
            # TODO: for some reason a shitload of dupilicate items are appearing here.
            if query['filter'] == 'all':
                items.append(item)
            else:
                if item.type == query['filter']:
                    items.append(item)

    return items


def filter_tags_if_people(query, items):
    result = []

    items = set(items)
    for item in items:
        for tag in item.tags:
            if tag.name in query['filter_people'].split(' '):
                if tag.name == '':
                    pass
                else:
                    result.append(item)
    return result


def get_query(session, userquery):
    query = construct_query_dict(userquery)
    tags = get_tags_from_query(session, query)
    items = filter_tags(query, tags)

    # if [filter] == people further filter with [people_tags]
    if query['filter'] == 'people':
        if query['filter_people'] != '':
            return set(filter_tags_if_people(query, items))

    return set(items)
# user query end


class Item():
    """Constructs a generic :class:`Item`"""
    # TODO: IMP function `get_query` into here somewhere.
    def __init__(self, session):
        self.session = session

    def get(self, id=None, query=None, filter=None):
        print('USING GLANCE_API.MODULES.FUNCTIONS.ITEM')
        """get item.

        id: primary key of database item, `None` returns all
        filter: item_type of database item, limit results to item_type
        """
        print(id)
        print(query)
        print(filter)

        if id:
            item = self.session.query(glance_api.modules.models.Item).get(id)
            return item

        elif query:
            print('enter query')
            items = self.session.query(glance_api.modules.models.Item).all()
            return items

        else:
            if filter == None or filter == 'all':
                items = self.session.query(glance_api.modules.models.Item).all()
                return items
            else:
                items = self.session.query(glance_api.modules.models.Item).filter(glance_api.modules.models.Item.type==filter).all()
                return items

    def delete(self, id):
        """ deletes item from database.

        id: primary key of database item,
        """
        item = self.session.query(glance_api.modules.models.Item).filter_by(id='{}'.format(int(id))).first()

        # TODO: strange bug using session.delete() it deletes the item and throws
        # as error item=None. wrapped it try/except fix it.
        try:
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


            self.session.delete(item)
        except:
            pass

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
            if 'items' in payload and payload['items'] != None:
                for x in payload['items'].split(' '):
                    item.items.append(self.session.query(glance_api.modules.models.Item).get(x))

        self.session.add(item)
        self.session.commit()


        # prepare tags for item

        # after entry is commited then hit the database with any new tags?
        # is this the best way?
        if 'tags' in payload and payload['tags'] != None:
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
            if k == 'collections' and v != None:
                query[k] = v.split()
            elif k == 'collection_rename' and v != None:
                query[k] = v
            elif k == 'append_to_collection' and v != None:
                query[k] = v
            elif k == 'items' and v != None:
                query[k] = v.split()
            elif k == 'tags' and v != None:
                query['tags'] = v.split()
            elif k == 'people_tags' and v != None:
                query[k] = v.split(' ')
            else:
                query[k] = v

        # once all user data is validated and ready to append, get asset object.
        asset = self.session.query(glance_api.modules.models.Item).get(id)
        # Process user data and update asset object fields.
        # TODO: is there a better way to handle these sort of 'flags'?
        for k, v in query.items():
            if k == 'name' and v != None:
                asset.name = v

            elif k == 'item_loc' and v != None:
                asset.item_loc = v

            elif k == 'collection_rename' and v != None:
                asset.name = v

            elif k == 'item_thumb' and v != None:
                asset.item_thumb = v

            elif k == 'append_to_collection' and v != None:
                collection = self.session.query(glance_api.modules.models.Item).get(v)
                collection.items.append(asset)

            elif k == 'attached' and v != None:
                asset.attached = v

            elif k == 'tags' and v != None:
                asset_tags = [x.name for x in asset.tags]

                user_input_tags = list(set(v))
                add_tag = []
                remove_tag = []
                people_tag = []

                for tag in user_input_tags:
                    if tag.startswith('-'):
                        remove_tag.append(tag)
                    else:
                        add_tag.append(tag)

                for tag in add_tag:
                    # create new Tag object and append to asset object
                    newtag = glance_api.modules.models.Tag(name=str(tag))
                    self.session.add(newtag)

                    asset.tags.append(newtag)

                for tag in remove_tag:
                    for x in asset.tags:
                        if x.name == tag[1:]:
                            self.session.delete(x)
                            self.session.commit()

            elif k == 'people_tags' and v != None:
                current_people_tags = [x for x in asset.tags if x.name.startswith('_')]
                print(current_people_tags)
                print(v)

                for x in current_people_tags:
                    if x.name not in v:
                        self.session.delete(x)

                for x in v:
                    new_tag = glance_api.modules.models.Tag(name=str(x))
                    self.session.add(new_tag)

                    asset.tags.append(new_tag)




            elif k == 'items' and v != None:
                # process asset tags
                for item in v:
                    item_to_collection = self.session.query(glance_api.modules.models.Item).get(int(item))
                    asset.items.append(item_to_collection)
                    self.session.add(asset)

            elif k == 'flag' and v != None:
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

            elif k == 'collections' and v != None:
                for collection_id in query['collections']:
                    # get Collection object using collection.id
                    existingcollection = self.session.query(glance_api.modules.models.Collection).get(collection_id)
                    # append existing collection to assets collections
                    asset.collections.append(existingcollection)

            else:
                pass

        # Finish asset object
        # append object moddate
        asset.moddate = str(datetime.datetime.utcnow())

        self.session.add(asset)
        self.session.commit()

        # Returns asset object
        return asset


    def __repr__(self):
        return '<Item>'
