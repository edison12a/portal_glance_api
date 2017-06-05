import sqlalchemy
from ..config import cred


engine = create_engine(
    'postgresql://{}:{}@{}:5432/{}'.format(
        cred.username, cred.password, cred.ip_local, cred.dev_db_name
    ), echo=False
)

Session = sessionmaker(bind=engine)

class Item():
    def __init__(self, item_type):
        self.item_type = item_type

    def get(id):
        return 'got an id'

    def __repr__(self):
        return '<Item>'
