"""
glance, exmaple `cred.py`
"""

__author__ = ""
__version__ = ""
__license__ = ""


import os

# Glance api
api_root = 'http://localhost:5050/glance/api/'

# flask
secret_key = os.urandom(12)

# AWS credentials
AWS_ACCESS_KEY_ID='AWS_ACCESS_KEY'
AWS_SECRET_ACCESS_KEY='AWS_SECRET_ACCESS_KEY'
AWS_BUCKET='BUCKET_NAME'
