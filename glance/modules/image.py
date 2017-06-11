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


def get_people_tags(data):

    list_of_people_tags = [x for x in data if x.startswith('_')]
    bla = structure_people_tags()

    for x in bla:
        for g in bla[x]:
            if g in list_of_people_tags:
                bla[x][g] = 1
            else:
                bla[x][g] = 0

    result = structure_people_tags()

    return bla


def update_people_tags(data):
    # get current tags
    pass


# support structures
def structure_people_tags():
    return {
        "num_people": {
            "_one": 0,
            "_couple": 0,
            "_group": 0,
        },
        "gender" : {
            "_male": 0,
            "_female": 0,
        },
        "age": {
            "_baby": 0,
            "_child": 0,
            "_teen": 0,
            "_adult": 0,
            "_senior": 0,
        },
        "ethnicity": {
            "_caucasian": 0,
            "_asian": 0,
            "_african": 0,
            "_middleeast": 0,
            "_indian": 0,
        },
        "camera": {
            "_back": 0,
            "_backangle": 0,
            "_side": 0,
            "_frontangle": 0,
            "_front": 0,
            "_above": 0,
            "_eyelevel": 0,
            "_below": 0,
        },
        "lightsource": {
            "_above_l": 0,
            "_back_l": 0,
            "_front_l": 0,
            "_side_l": 0,
            "_below_l": 0,
        },
        "lightgeneral": {
            "_sunlight": 0,
            "_ambient": 0,
            "_shade": 0,
            "_backlit": 0,
        },
        "season": {
            "_summer": 0,
            "_autumn": 0,
            "_spring": 0,
            "_winter": 0,
        },
        "activity": {
            "_standing": 0,
            "_sitting": 0,
            "_playing": 0,
            "_running": 0,
            "_riding": 0,
            "_workout": 0,
            "_lying": 0,
        },
        "style": {
            "_casual": 0,
            "_resort": 0,
            "_sports": 0,
            "_religious": 0,
            "_alternative": 0,
            "_business": 0,
            "_medical": 0,
            "_uniform": 0,
            "_formal": 0,
            "_work": 0,
        }
    }
