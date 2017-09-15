import configparser
import os
from pathlib import Path

# parser setup
config = configparser.ConfigParser()
# get config file.
# the if below checks wether this .py is being run by sphinx or not.
# TODO: a better fix for here could be just setting the cwd to project root?
project_root = Path(os.path.dirname(__file__)).parent
config.read(os.path.join(project_root, 'config', 'config.ini'))

# select config type
config_type = config['dev']

# flask settings
secret_key = config_type['secretkey']
api_root = config_type['api_entry']
tmp_upload = os.path.join(project_root, 'static', 'tmp')
