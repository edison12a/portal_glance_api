"""
This module describes the database using sqlalchemy. declaritive.
"""

__author__ = ""
__version__ = ""
__license__ = ""

import datetime

from sqlalchemy import (
    Column, func, Integer, Table, String, ForeignKey, DateTime
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

tag_ass = Table('tag_association_table', Base.metadata,
    Column('tag_id', Integer, ForeignKey('tag.id')),
    Column('item_id', Integer, ForeignKey('item.id'))
)
# association table: Collection.id, Asset.id
collect_ass = Table('collection_association_table', Base.metadata,
    Column('collection_id', Integer, ForeignKey('collection.id')),
    Column('item_id', Integer, ForeignKey('item.id'))
)


class Account(Base):
    """Account Table"""
    __tablename__ = "account"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    initdate = Column(String, default=str(datetime.datetime.utcnow()))


    def __init__(self, username, password):

        self.username = username
        self.password = password


class Tag(Base):
    """Tag Table"""
    # TODO: I think all asset databases should be replaced with a 'all assets'
    # table.
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    items = relationship("Item",
                    secondary=tag_ass,
                    backref="tags")

    def __repr__(self):
        return "<Tag(name={})>".format(self.name)


# inherited tables test
class Item(Base):
    """Item Table
    Master table. Item types inherit from Item.
    """
    # This class also has a tags variable. From `class Tag:item` many to many
    # relationship
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'item',
        'polymorphic_on': type
    }


class Image(Item):
    """Image Table
    Inherits from Item.
    """
    __tablename__ = 'image'

    id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    name = Column(String)
    item_loc = Column(String)
    item_thumb = Column(String)
    flag = Column(Integer, default=0)
    author = Column(String)
    initdate = Column(DateTime, default=func.now())
    moddate = Column(DateTime, default=func.now())
    item_type = Column(String, default=__tablename__)
    attached = Column(String, default=None)

    # TODO: IMP relationships with collections and tags

    __mapper_args__ = {
        'polymorphic_identity': 'image'
    }


class Footage(Item):
    """Footage Table
    Inherits from Item.
    """
    __tablename__ = 'footage'

    id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    name = Column(String)
    item_loc = Column(String)
    item_thumb = Column(String)
    flag = Column(Integer, default=0)
    author = Column(String)
    initdate = Column(DateTime, default=func.now())
    moddate = Column(DateTime, default=func.now())
    item_type = Column(String, default=__tablename__)
    attached = Column(String, default=None)

    __mapper_args__ = {
        'polymorphic_identity': 'footage'
    }


class Geometry(Item):
    """Geoemtry Table
    Inherits from Item.
    """
    __tablename__ = 'geometry'

    id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    name = Column(String)
    item_loc = Column(String)
    item_thumb = Column(String)
    flag = Column(Integer, default=0)
    author = Column(String)
    initdate = Column(DateTime, default=func.now())
    moddate = Column(DateTime, default=func.now())
    item_type = Column(String, default=__tablename__)
    attached = Column(String, default=None)

    __mapper_args__ = {
        'polymorphic_identity': 'geometry'
    }


class People(Item):
    """People Table
    Inherits from Item.
    """
    __tablename__ = 'people'

    id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    name = Column(String)
    item_loc = Column(String)
    item_thumb = Column(String)
    flag = Column(Integer, default=0)
    author = Column(String)
    initdate = Column(DateTime, default=func.now())
    moddate = Column(DateTime, default=func.now())
    item_type = Column(String, default=__tablename__)
    attached = Column(String, default=None)

    __mapper_args__ = {
        'polymorphic_identity': 'people'
    }


class Collection(Item):
    """Collection Table
    Inherits from Item.
    """
    __tablename__ = 'collection'

    id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    name = Column(String)
    item_loc = Column(String)
    item_thumb = Column(String)
    flag = Column(Integer, default=0)
    author = Column(String)
    initdate = Column(DateTime, default=func.now())
    moddate = Column(DateTime, default=func.now())
    item_type = Column(String, default=__tablename__)
    attached = Column(String, default=None)

    items = relationship("Item",
                    secondary=collect_ass,
                    backref="collections")

    __mapper_args__ = {
        'polymorphic_identity': 'collection'
    }
