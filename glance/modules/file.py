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
import glance.app
import glance.modules.api

ALLOWED_FILE_TYPES = ['.jpg', '.zip', '.mp4']

def upload_handler(dst, filelist, account_session, item_type):
    if isinstance(filelist, list):
        pass
    else:
        filelist = [filelist]

    for file in filelist:
        try:
            dst, root, ext = local_save_file(dst, file)
        except:
            return False

        if item_type == None:
            # edge case: change collection cover.
            dst, filename, thumbnail = local_make_thumbnail(dst, root, ext)
            local_file_to_s3.apply_async((dst, filename), link=local_clean_up.si(dst, filename))
            local_file_to_s3.apply_async((dst, thumbnail), link=local_clean_up.si(dst, thumbnail))

            return (filename, thumbnail)


        if ext == '.jpg' or ext == '.mp4':
            dst, filename, thumbnail = local_make_thumbnail(dst, root, ext)

            payload = {'name': root, 'item_loc': filename, 'item_thumb': thumbnail, 'item_type': item_type}
            res = glance.modules.api.post_item(account_session, payload)

            # below celery task needs to imp rek with db update
            local_file_to_s3.apply_async((dst, filename), link=[aws_rek_image.si(res[0]['id'], filename, account_session), local_clean_up.si(dst, filename)])
            local_file_to_s3.apply_async((dst, thumbnail), link=local_clean_up.si(dst, thumbnail))

        if ext == '.zip':
            filename = f'{root}{ext}'
            local_file_to_s3.apply_async((dst, filename), link=local_clean_up.si(dst, filename))

        return res


def local_save_file(dst, fileobj):
    root, ext = os.path.splitext(fileobj.filename)
    if ext not in ALLOWED_FILE_TYPES:
        # TODO: IMP error
        return False

    root, ext = local_rename_file_with_salt(root, ext)
    fileobj.save(os.path.join(dst, '{}{}'.format(root, ext)))

    return (dst, root, ext)


def local_rename_file_with_salt(root, ext):
    salt = secrets.token_urlsafe(4)
    root = '{}_{}'.format(root, salt)

    return (root, ext)


def local_make_thumbnail(dst, root, ext):
    if ext == '.jpg':
        thumbnail = image.thumb(dst, f'{root}{ext}')

    elif ext == '.mp4':
        saved_frame = image.save_frame(dst, f'{root}{ext}')
        thumbnail = image.thumb(dst, saved_frame)
    
    else:
        return False

    return (dst, f'{root}{ext}', thumbnail)

@glance.app.celery.task
def local_file_to_s3(dst, filename):
    s3 = auth.boto3_res_s3()
    auth.boto3_s3_upload(s3, dst, filename)

    return (dst, filename)

@glance.app.celery.task
def local_clean_up(dst, filename):
    os.remove(os.path.join(dst, filename))

    return filename


@glance.app.celery.task
def aws_rek_image(id, filename, account_session):
    tags = []
    for tag in image.generate_tags(filename):
        tags.append(tag.lower())

    if len(tags) > 0:
        payload = {'id': id, 'tags': ' '.join(tags)}
        glance.modules.api.put_item(account_session, payload)

    return True


# TODO: IMP celery for create_payload, and aws rekignition
def create_payload(account_session, upload_data, item_name, **files):
    """"""
    payload = {}
    payload['name'] = item_name
    payload['author'] = account_session['username']
    payload['tags'] = upload_data['tags']
    payload['item_type'] = upload_data['itemradio']
    payload['item_loc'] = files['filename']
    payload['item_thumb'] = files['thumbnail']
    if 'attachment' in files and files['attachment']:
        payload['attached'] = files['attachment']

    """
    # AWS REKOGNITION
    for tag in image.generate_tags(files['filename']):
        if payload['tags'] == '':
            payload['tags'] = tag.lower()
        else:
            payload['tags'] += ' ' + tag.lower()
    """

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
