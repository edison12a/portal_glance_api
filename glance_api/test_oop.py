from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from config import settings


engine = create_engine(settings.DEV_POSTGRES_DATABASE, echo=False)

Session = sessionmaker(bind=engine)

class Item():
    def __init__(self):
        pass

    def get(id):

        return 'got an id'

    def itemtype():
        return

    def __repr__(self):
        return '<Item>'

test = Item()
print(test)
