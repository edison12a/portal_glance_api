import os
import requests
import io
import boto3

from PIL import Image, ImageChops, ImageOps, ImageDraw


from config import cred

# universal file directory
# item_storage = os.path.join(os.path.expanduser('~'), "glance_storage", "media", "asset")


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
