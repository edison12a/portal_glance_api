import os

from flask import send_from_directory
import requests
import boto3

from config  import cred


# CONFIG
BASEURI = 'http://127.0.0.1:5050'
API = 'http://127.0.0.1:5050/glance/api'


def LoggedIn(session):
    if session.get('logged_in'):

        return True
    else:

        return False


def CheckLoginDetails(**data):
    r = requests.get('{}/user'.format(API), params=data)

    if 'user details' in r.json():
        if r.json()['user details']:
            result = True
        else:
            result = False
    else:
        # TODO: if this is an error, it could be explained better.
        result = False

    return result

def upload_handler(file, dst):
    # TODO: Figure out where to handle auto thumbnailing.
    filename = file.filename
    file.save(os.path.join(dst, filename))

    boto3_session = boto3.session.Session(
        aws_access_key_id=cred.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=cred.AWS_SECRET_ACCESS_KEY,
    )

    s3 = boto3_session.resource('s3')

    data = send_from_directory(dst, filename)
    s3.Object(cred.AWS_BUCKET, filename).put(Body=open(os.path.join(dst, filename), 'rb'))

    os.remove(os.path.join(dst, filename))
