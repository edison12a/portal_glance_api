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


def get_bucket(access_key_id, secret_access_key, bucket_name):
    conn = boto.connect_s3(access_key_id, secret_access_key)
    return conn.get_bucket(bucket_name)


def upload_handler(instance, file_obj):
    # access our S3 bucket and create a new key to store the file data
    bucket = get_bucket(cred.AWS_ACCESS_KEY_ID, cred.AWS_SECRET_ACCESS_KEY, cred.AWS_BUCKET)
    key = bucket.new_key(instance.filename)
    key.set_metadata('Content-Type', instance.mimetype())

    # seek to the beginning of the file and read it into the key
    file_obj.seek(0)
    key.set_contents_from_file(file_obj)

    # make the key publicly available
    key.set_acl('public-read')
