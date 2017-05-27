"""
This module contains functions for Image Processing
"""

__author__ = ""
__version__ = ""
__license__ = ""

import os

from PIL import Image, ImageOps
import subprocess
import boto3

import modules.auth as auth


'''Globals'''
API = 'http://127.0.0.1:5050/glance/api'


# AWS Rekognition
def generate_tags(data):
    client = auth.boto3_res_rek()
    response = auth.boto3_rek_tag(client, data)

    result = [x['Name'] for x in response['Labels']]


    return result


def thumb(filename, dir):
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
