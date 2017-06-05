"""
glance api
"""

__author__ = ""
__version__ = ""
__license__ = ""

from config import cred

# global
ROUTE = '/glance/api'

# dev
DEV_POSTGRES_DATABASE = 'postgresql://{}:{}@{}:{}/{}'.format(
    cred.username, cred.password, cred.dev_postgres_ip, cred.dev_postgres_port, cred.dev_postgres_name
)

DEV_DATABASE_HOST = 'http://{}:{}/'.format(cred.dev_postgres_ip, cred.dev_postgres_port)
DEV_API_ENTRY = '{}{}'.format(DEV_DATABASE_HOST, ROUTE)

# prod
PROD_POSTGRES_DATABASE = 'postgresql://{}:{}@{}:{}/{}'.format(
    cred.username, cred.password, cred.prod_postgres_ip, cred.prod_postgres_port, cred.prod_postgres_name
)

PROD_DATABASE_HOST = 'http://{}:{}/'.format(cred.prod_postgres_ip, cred.prod_postgres_port)
PROD_API_ENTRY = '{}{}'.format(PROD_DATABASE_HOST, ROUTE)
