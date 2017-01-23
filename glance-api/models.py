import datetime

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

import cred


# Database models
Base = declarative_base()

class Collection(Base):
    # TODO: Better repr
    __tablename__ = 'test_collection'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    image = Column(String)
    image_thumb = Column(String)
    tag = Column(postgresql.ARRAY(String))
    flag = Column(Integer, default=0)
    author = Column(String)
    initdate = Column(Date, default=datetime.datetime.utcnow())
    moddate = Column(Date, default=datetime.datetime.utcnow())
    # relational data
    assets = relationship(
        "Asset", back_populates='collection',
        cascade="all, delete, delete-orphan"
    )

    def __repr__(self):
        return "<Collection(name='%s', image='%s', assets='%s')>" % (
            self.name, self.image, self.assets
        )


class Asset(Base):
    # TODO: Better repr
    __tablename__ = 'test_asset'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    image = Column(String)
    image_thumb = Column(String)
    attached = Column(String)
    tag = Column(postgresql.ARRAY(String))
    flag = Column(Integer, default=0)
    author = Column(String)
    initdate = Column(Date, default=datetime.datetime.utcnow())
    moddate = Column(Date, default=datetime.datetime.utcnow())
    # relational data
    collection_id = Column(Integer, ForeignKey('test_collection.id'))
    collection = relationship("Collection", back_populates="assets")

    def __repr__(self):
        return "<Asset(id='%s', name='%s')>" % (
            self.id, self.name
        )


# Int sqlalchemy engine
engine = create_engine(
    'postgresql://{}:{}@{}:5432/glance'.format(
        cred.username, cred.password, cred.ip
    ),
    echo=False
)

# Init sessionmaker
Session = sessionmaker(bind=engine)

# Init session
session = Session()

# private functions
def reset_db(session, engine=engine):
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
def post_collection(session, **user_columns):
    """ POST: Collection"""
    print(user_columns)
    # TODO: Once collection table is finished update this function.
    # Approved query
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
    for column in collection_columns:
        # if user data does include all database columns. There are added to
        # approve query variable and padded with 'None'
        if column not in user_columns and column != 'id':
            query[column] = None

    # TODO: Validate assets?
    # Append user assets to approved query
    try:
        query['assets'] = user_columns['assets']
    except KeyError:
        query['assets'] = []

    # create new collection and commit to database
    collection = Collection(
        name=query['name'], image=query['image'],
        image_thumb=query['image_thumb'], tag=query['tag'],
        author=query['author'], assets=query['assets']
    )
    session.add(collection)
    session.commit()
    session.close()

    return collection


def post_asset(session, **user_columns):
    """ POST: Asset"""
    # TODO: Once asset table is finished update this function.
    # Approved query
    # TODO: Figure out how to use arrays with ORM. i.e. collection_ids

    query = {}
    # Check user columns
    asset_columns = Asset.__table__.columns.keys()
    # compare user column data to database columns
    for k, v in user_columns.items():
        if k in asset_columns:
            # if match append user data to approved query variable
            query[k] = v
        else:
            pass
    for column in asset_columns:
        # if user data does include all database columns. There are added to
        # approve query variable and padded with 'None'
        if column not in user_columns and column != 'id':
            query[column] = None

    # create new asset and commit to database
    asset = Asset(
        name=query['name'], image=query['image'],
        collection_id=query['collection_id'], tag=query['tag'], attached=query['attached'],
        author=query['author'], image_thumb=query['image_thumb']
    )
    session.add(asset)
    session.commit()

    return asset


def get_collections(session):
    """Returns all collection objects"""
    collections = []
    for instance in session.query(Collection).order_by(Collection.id):
        collections.append(instance)

    return collections


def get_assets(session):
    """Returns all asset objects"""
    assets = []
    for instance in session.query(Asset).order_by(Asset.id):
        assets.append(instance)

    return assets


def get_asset_by_id(session, id):
    """Return asset object using id"""
    asset_by_id = session.query(Asset).get(id)

    return asset_by_id


def get_collection_by_id(session, id):
    """Returns collection object using id"""
    collection_by_id = session.query(Collection).get(id)

    return collection_by_id


def get_query(session, *query):
    """takes list of words and returns related objects"""

    test = session.query(Asset).filter(Asset.tag.any(query[0])).all()

    print(test)

    pass

bla = ['whaaa']
get_query(session, bla)

print(get_asset_by_id(session, 1))


def patch_asset(session, id, **user_columns):
    """patches users defined columns with user defined values"""
    query = {}
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
            asset.tag = v
        elif k == 'flag':
            if query['flag'] == 1:
                try:
                    asset.flag += 1
                except TypeError:
                    asset.flag = 0
                    asset.flag += 1
            elif query['flag'] == 0:
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


# reset db
# reset_db(session, engine)
