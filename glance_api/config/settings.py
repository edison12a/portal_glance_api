"""
glance api
"""

__author__ = ""
__version__ = ""
__license__ = ""

import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.join('config', 'config.ini'))

# global
config_type = config['dev']
ROUTE = '/glance/api'

POSTGRES_DATABASE = 'postgresql://{}:{}@{}:{}/{}'.format(
    config_type['username'], config_type['password'],
    config_type['postgresIP'], config_type['postgresPort'],
    config_type['postgresName']
)
