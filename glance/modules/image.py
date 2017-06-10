"""
This module contains functions for Image Processing
"""

__author__ = ""
__version__ = ""
__license__ = ""

import os
import subprocess

from PIL import Image, ImageOps
import boto3

import glance.modules.auth as auth
import glance.config.settings as settings


# AWS Rekognition
def generate_tags(data):
    """Using AWS Rekognition, generate tags (labels).

    :param data: -- ???

    :return type: ???
    """
    client = auth.boto3_res_rek()
    response = auth.boto3_rek_tag(client, data)

    result = [x['Name'] for x in response['Labels']]

    return result


def thumb(dir, filename):
    """Generate thumbnail from file.

    :param dir: -- ???
    :param filename: -- ???

    :return type: ???
    """
    im = Image.open('{}/{}'.format(dir, filename))
    file, ext = os.path.splitext(filename)
    # correct jpg naming to jpeg
    if ext == '.jpeg':
        ext = '.jpg'
    else:
        pass

    size = (200, 200)
    thumb = ImageOps.fit(im, size, Image.LANCZOS)

    output_file_name = '{}_thumbnail{}'.format(file, ext)
    thumb.save('{}/{}'.format(dir, output_file_name))

    return output_file_name


def save_frame(dst, file):
    """Extract frame from mp4.

    :param dst: -- ???
    :param file: -- ???

    :return type: ???
    """
    filename, ext = os.path.splitext(file)
    saved_frame_loc = '{}/{}.jpg'.format(dst, filename)

    # run external software server side to rip a frame of the video file
    # and save it.
    subprocess.call(
        'ffmpeg -ss 0.5 -i {}/{} -t 1 {}'.format(dst, file, saved_frame_loc),
        shell=True
    )

    file_saved_frame = saved_frame_loc.split('/')[-1:][0]

    return file_saved_frame
