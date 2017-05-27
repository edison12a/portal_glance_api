"""
This module contains functions for Authentication & Authorization
"""

__author__ = ""
__version__ = ""
__license__ = ""

import os
import requests
import boto3

from config import cred


'''Globals'''
API = 'http://127.0.0.1:5050/glance/api'

# basic unencrypted user auth using the api and flasks `session`.
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


# aws access
def boto3_res_s3():
    boto3_session = boto3.session.Session(
        aws_access_key_id=cred.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=cred.AWS_SECRET_ACCESS_KEY,
    )

    s3 = boto3_session.resource('s3')

    return s3


def boto3_res_rek():
    boto3_session = boto3.session.Session(
        aws_access_key_id=cred.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=cred.AWS_SECRET_ACCESS_KEY,
    )

    # init client
    client = boto3_session.client('rekognition', region_name='us-east-1')

    return client


def boto3_rek_tag(data, confidence=60):
    result = client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': cred.AWS_BUCKET,
                'Name': data,
            },
        },
        MaxLabels=100,
        MinConfidence=confidence,
    )

    return result


def boto3_s3_upload(s3, dst, file):
    s3.Object(cred.AWS_BUCKET, file).put(Body=open(os.path.join(dst, file), 'rb'))

    return file


def delete_from_s3(data):
    # refactor below
    # get s3 resource
    # TODO: dont not delete thumbnail?
    s3 = boto3_res_s3()

    bucket = s3.Bucket(cred.AWS_BUCKET)

    objects_to_delete = []
    for obj in data:
        objects_to_delete.append({'Key': obj})

    bucket.delete_objects(
        Delete={
            'Objects': objects_to_delete
        }
    )
