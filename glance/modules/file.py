"""
This module contains functions for Files
"""

__author__ = ""
__version__ = ""
__license__ = ""

import os
import secrets

import boto3

import glance.modules.image as image
import glance.modules.auth as auth


def upload_handler(file, dst):
    """handles uploading of all files
    Returns: var result, list. List of Processed `file` and any additional files
    made. thumbnail, video frames...
    """
    # data structures
    items = []
    result = []
    allowed = ['.jpg', '.zip', '.mp4']
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

        if ext == '.jpg':
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

    return collector


    return True
