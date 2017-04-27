# TODO: Implement proper config, include auth to replace 'import cred'
from sqlalchemy import (
    Column, func, Integer, Table, String, ForeignKey, DateTime
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship



# Database models
Base = declarative_base()

'''
"""association tables"""
# association table: Collection.id, Asset.id
assignment = Table('assignment', Base.metadata,
    Column('collection_id', Integer, ForeignKey('collection.id')),
    Column('asset_id', Integer, ForeignKey('asset.id'))
)

# association table: Tag.id, Asset.id, Collection.id
# TODO: I think many-to-manys should link 3 classes? perhaps theres a better
# way maybe an additional 'all objects table' so everything have a unique id?
tag_table = Table('tag_table', Base.metadata,
    Column('tag_id', Integer, ForeignKey('tag.id')),
    Column('asset_id', Integer, ForeignKey('asset.id')),
    Column('collection_id', Integer, ForeignKey('collection.id'))
)
'''
"""declarative tables"""

'''
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
        secondary=tag_table, back_populates='collection_tags'
    )

    def __repr__(self):
        return "<Collection(name='%s', image='%s')>" % (
            self.name, self.image
        )
'''
'''
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
        secondary=tag_table, back_populates='item'
    )

    def __repr__(self):
        return "<Asset(id='%s', name='%s')>" % (
            self.id, self.name
        )
'''
"""
class Footage(Base):
    # Footage database structure, declarative
    # TODO: Better repr
    # TODO: IMP tags for footage? consider changing who the tag table works?
    # TODO: IMP collections for footage? consider changing who the tag table works?
    __tablename__ = 'footage'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    footage = Column(String)
    image_thumb = Column(String)
    flag = Column(Integer, default=0)
    author = Column(String)
    initdate = Column(DateTime, default=func.now())
    moddate = Column(DateTime, default=func.now())
    item_type = Column(String, default=__tablename__)

    collections = relationship("Collection",
        secondary=assignment
    )
    tags = relationship("Tag",
        secondary=tag_table, back_populates='item'
    )


    def __repr__(self):
        return "<Footage(id='%s', name='%s')>" % (
            self.id, self.name
        )
"""


tag_ass = Table('tag_association_table', Base.metadata,
    Column('tag_id', Integer, ForeignKey('tag.id')),
    Column('item_id', Integer, ForeignKey('item.id'))
)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)


    def __init__(self, username, password):

        self.username = username
        self.password = password


class Tag(Base):
    """Tag database structure, declarative"""
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

    def __repr__(self):
        return "<Image(id='%s', name='%s')>" % (
            self.id, self.name
        )


class Footage(Item):
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


class Collection(Item):
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

    __mapper_args__ = {
        'polymorphic_identity': 'collection'
    }
