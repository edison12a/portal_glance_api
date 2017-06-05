"""
glance, exmaple `cred.py`
"""

__author__ = ""
__version__ = ""
__license__ = ""


import os

# Glance api
api_detail = ['HOST_IP', 'HOST_POST']
API_HOST = 'http://{}:{}/'.format(api_detail[0], api_detail[1])

# flask
secret_key = os.urandom(12)

# AWS credentials
AWS_ACCESS_KEY_ID='AWS_ACCESS_KEY'
AWS_SECRET_ACCESS_KEY='AWS_SECRET_ACCESS_KEY'
AWS_BUCKET='BUCKET_NAME'
