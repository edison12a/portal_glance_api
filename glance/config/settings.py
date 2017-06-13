import configparser
import os

# global
config = configparser.ConfigParser()
config.read(os.path.join('config', 'config.ini'))

config_type = config['dev']

secret_key = config_type['secretkey']
api_root = config_type['route']
