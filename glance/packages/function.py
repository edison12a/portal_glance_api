import os
import subprocess
import secrets

from flask import send_from_directory
import requests
import boto3

from config  import cred


'''config'''
BASEURI = 'http://127.0.0.1:5050'
API = 'http://127.0.0.1:5050/glance/api'

# auth
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


# process
def upload_handler(file, dst):
    """handles uploading of all files"""
    # TODO: Figure out where to handle auto thumbnailing.
    # process filenames and add random characters to avoid duplication
    salt = secrets.token_urlsafe(4)
    filename, ext = os.path.splitext(file.filename)
    filename = '{}_{}'.format(filename, salt)

    file.save(os.path.join(dst, '{}{}'.format(filename, ext)))

    # refactor below
    boto3_session = boto3.session.Session(
        aws_access_key_id=cred.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=cred.AWS_SECRET_ACCESS_KEY,
    )

    s3 = boto3_session.resource('s3')

    data = send_from_directory(dst, '{}{}'.format(filename, ext))
    s3.Object(cred.AWS_BUCKET, '{}{}'.format(filename, ext)).put(Body=open(os.path.join(dst, '{}{}'.format(filename, ext)), 'rb'))

    if ext == '.mp4':
        # TODO: actual upload to aws needs to be refactored away

        footage_loc = '{}/{}{}'.format(dst, filename, ext)

        frame_save_loc = '{}/{}.jpg'.format(dst, filename)

        subprocess.call(
            'ffmpeg -ss 0.5 -i {} -t 1 {}'.format(footage_loc, frame_save_loc),
            shell=True
        )

        # refactor below
        boto3_session = boto3.session.Session(
            aws_access_key_id=cred.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=cred.AWS_SECRET_ACCESS_KEY,
        )

        s3 = boto3_session.resource('s3')

        s3.Object(cred.AWS_BUCKET, '{}.jpg'.format(filename)).put(Body=open(os.path.join(dst, '{}.jpg'.format(filename)), 'rb'))

        os.remove(os.path.join(dst, '{}.jpg'.format(filename)))


    os.remove(os.path.join(dst, '{}{}'.format(filename, ext)))

    return '{}{}'.format(filename, ext)


def process_raw_files(files):
    '''pair images and attachments'''
    collector = {}
    for x in files:
        filename, ext = os.path.splitext(x.filename)
        if filename not in collector:
            collector[filename] = []
            collector[filename].append(x)
        else:
            collector[filename].append(x)


    print('pppppppppp')
    print(collector)

    return collector


def item_to_session(session, *args):
    print(args)

    return session


def rektest(data):
    # TODO: Finish function
    # refactor below
    # init session with cred
    boto3_session = boto3.session.Session(
        aws_access_key_id=cred.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=cred.AWS_SECRET_ACCESS_KEY,
    )

    # init client
    client = boto3_session.client('rekognition', region_name='us-east-1')

    response = client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': 'glancestore',
                'Name': data,
            },
        },
        MaxLabels=100,
        MinConfidence=60,
    )

    test = [x['Name'] for x in response['Labels']]


    return test


def delete_from_s3(data):
    # refactor below
    boto3_session = boto3.session.Session(
        aws_access_key_id=cred.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=cred.AWS_SECRET_ACCESS_KEY,
    )

    s3 = boto3_session.resource('s3')
    bucket = s3.Bucket(cred.AWS_BUCKET)

    objects_to_delete = []
    for obj in data:
        objects_to_delete.append({'Key': obj})

    bucket.delete_objects(
        Delete={
            'Objects': objects_to_delete
        }
    )

    return True
