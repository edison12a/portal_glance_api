# TODO: Implement proper config, include auth to replace 'import cred'
from sqlalchemy import (
    Column, func, Integer, Table, String, ForeignKey, DateTime
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import cred


# Database models
Base = declarative_base()

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
        secondary=tag_table, back_populates='collection_tags'
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
        secondary=tag_table, back_populates='item'
    )

    def __repr__(self):
        return "<Asset(id='%s', name='%s')>" % (
            self.id, self.name
        )
