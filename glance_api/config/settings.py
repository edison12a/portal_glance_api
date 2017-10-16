import configparser
import os
from pathlib import Path

project_root = Path(os.path.dirname(__file__)).parent

config = configparser.ConfigParser()
config.read(os.path.join(project_root, 'config', 'config.ini'))

# global
config_type = config['dev']
ROUTE = '/glance/api'

POSTGRES_DATABASE = 'postgresql://{}:{}@{}:{}/{}'.format(
    config_type['username'], config_type['password'],
    config_type['postgresIP'], config_type['postgresPort'],
    config_type['postgresName']
)
