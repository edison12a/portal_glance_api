import os
import secrets

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
    """handles uploading of all files"""
    # TODO: Figure out where to handle auto thumbnailing.
    # process filenames and add random characters to avoid duplication
    salt = secrets.token_urlsafe(4)
    filename, ext = os.path.splitext(file.filename)
    filename = '{}_{}'.format(filename, salt)

    file.save(os.path.join(dst, '{}{}'.format(filename, ext)))

    boto3_session = boto3.session.Session(
        aws_access_key_id=cred.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=cred.AWS_SECRET_ACCESS_KEY,
    )

    s3 = boto3_session.resource('s3')

    data = send_from_directory(dst, '{}{}'.format(filename, ext))
    s3.Object(cred.AWS_BUCKET, '{}{}'.format(filename, ext)).put(Body=open(os.path.join(dst, '{}{}'.format(filename, ext)), 'rb'))

    os.remove(os.path.join(dst, '{}{}'.format(filename, ext)))

    return '{}{}'.format(filename, ext)


def process_raw_files(files):
    """pair images and attachments"""
    collector = {}
    for x in files:
        filename, ext = os.path.splitext(x.filename)
        if filename not in collector:
            collector[filename] = []
            collector[filename].append(x)

        else:
            collector[filename].append(x)

    return collector
