import configparser
import os

# global
config = configparser.ConfigParser()

# the if below checks wether this .py is being run by sphinx or not.
# TODO: a better fix for here could be just setting the cwd to project root?
cwd = os.getcwd()
if os.getcwd().endswith('docs'):
    loc = os.getcwd()[:-5]
    config.read(os.path.join(loc, 'glance', 'config', 'config.ini'))
else:
    config.read(os.path.join('config', 'config.ini'))

config_type = config['dev']

secret_key = config_type['secretkey']
api_root = config_type['api_entry']
