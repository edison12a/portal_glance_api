"""
This module contains functions for Files
"""

__author__ = ""
__version__ = ""
__license__ = ""

import os
import secrets
import string

import glance.modules.image as image
import glance.modules.auth as auth


def upload_handler(file, dst):
    """handles uploading of all file types.

    :param file: ???
    :param dst: ???

    :return Type: ???
    """
    # data structures
    items = []
    result = []
    allowed = ['.jpg', '.zip', '.mp4', '.png']
    # process filenames and add random characters to avoid duplication, and
    filename, ext = os.path.splitext(file.filename)

    # check if `file` is allowed, else...
    if ext not in allowed:
        # TODO: IMP error
        return False

    # save locally for 'physical' processing.
    salt = secrets.token_urlsafe(4)
    filename = '{}_{}'.format(filename, salt)
    file.save(os.path.join(dst, '{}{}'.format(filename, ext)))


    items.append('{}{}'.format(filename, ext))
    # result.append('{}{}'.format(filename, ext))

    # get s3 resource
    s3 = auth.boto3_res_s3()

    # process each file based on extention. Any file extentions not allowed
    # are ignored.
    for item in items:
        filename, ext = os.path.splitext(item)

        if ext == '.jpg' or ext == '.png':
            # Make thumbnail and upload items to s3
            thumbnail = image.thumb(dst, '{}{}'.format(filename, ext))
            auth.boto3_s3_upload(s3, dst, item)
            auth.boto3_s3_upload(s3, dst, thumbnail)

            result.append('{}{}'.format(filename, ext))
            result.append(thumbnail)
            # clean up local
            os.remove(os.path.join(dst, item))
            os.remove(os.path.join(dst, thumbnail))


            return result


        elif ext == '.zip':
            # upload zip file
            auth.boto3_s3_upload(s3, dst, item)

            result.append('{}{}'.format(filename, ext))
            # clean up
            os.remove(os.path.join(dst, item))


            return result


        elif ext == '.mp4':
            # get frame from  video file and upload all
            saved_frame = image.save_frame(dst, '{}{}'.format(filename, ext))
            thumbnail_from_saved_frame = image.thumb(dst, saved_frame)

            auth.boto3_s3_upload(s3, dst, item)
            auth.boto3_s3_upload(s3, dst, thumbnail_from_saved_frame)

            result.append(item)
            result.append(thumbnail_from_saved_frame)
            # Clean up
            os.remove(os.path.join(dst, item))
            os.remove(os.path.join(dst, saved_frame))
            os.remove(os.path.join(dst, thumbnail_from_saved_frame))

            return result

        else:
            # TODO: error
            pass


    # `TODO: error
    return result

def create_payload(account_session, upload_data, item_name, uploaded_file):
    """"""
    payload = {}
    payload['name'] = item_name
    payload['author'] = account_session['username']
    payload['tags'] = upload_data['tags']
    payload['item_type'] = upload_data['itemradio']
    payload['item_loc'] = uploaded_file[0]
    payload['item_thumb'] = uploaded_file[1]

    # AWS REKOGNITION
    for tag in image.generate_tags(uploaded_file[0]):
        if payload['tags'] == '':
            payload['tags'] = tag.lower()
        else:
            payload['tags'] += ' ' + tag.lower()

    # Process image name
    payload_name = ''
    for x in payload['name']:
        if x == '_' or x == '-':
            payload_name += ' '
            pass
        elif x in string.punctuation:
            pass
        else:
            payload_name += x

    # apend payload_name to tag string for posting.
    if payload['tags'] == '':
        payload['tags'] = payload_name.lower()
    else:
        payload['tags'] += ' {}'.format(payload_name.lower())

    return payload


def process_raw_files(files):
    """pairs images to attachments.

    :param files: ???

    :return Type: ???
    """
    collector = {}
    for x in files:
        filename, ext = os.path.splitext(x.filename)
        if filename not in collector:
            collector[filename] = []
            collector[filename].append(x)
        else:
            collector[filename].append(x)

    return collector
