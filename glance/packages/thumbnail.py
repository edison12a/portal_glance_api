import os
import requests
import io
import boto3

from PIL import Image, ImageChops, ImageOps, ImageDraw


from config import cred

# universal file directory
# item_storage = os.path.join(os.path.expanduser('~'), "glance_storage", "media", "asset")


def thumb(filename, dir):
    # response = requests.get('https://s3.amazonaws.com/{}/{}'.format(AWS_BUCKET, filename), stream=True)
    # return Image.open(StringIO.StringIO(response.content))
    # im = Image.open(io.BytesIO(response.content))
    im = Image.open('{}/{}'.format(dir, filename))
    file, ext = os.path.splitext(filename)
    # correct jpg naming to jpeg
    """
    if ext == '.jpg':
        ext = '.jpeg'
    else:
        pass
    """

    size = (200, 200)
    im.thumbnail(size, Image.ANTIALIAS)

    output = io.BytesIO()
    thumb = ImageOps.fit(im, size, Image.ANTIALIAS)

    output_file_name = '{}_thumbnail{}'.format(file, ext)
    thumb.save('{}/{}'.format(dir, output_file_name))

    # return (file, ext)
    return output_file_name


    # Once image is uploaded and saved. A Thumbnail is created.
def img_Thumb(filename):
    """Opens image, makes thumbnail, saves to dir and returns filename plus
    extension in a tuple.
    Atti: filename takes the name of an image file.
    Bug:
    Eventually extend this to a class to include all image processing.
    """
    test = True
    if test == False:
        im = Image.open(os.path.join(item_storage, filename))

        file, ext = os.path.splitext(filename)
        size = (200, 200)
        im.thumbnail(size, Image.ANTIALIAS)

        thumb = ImageOps.fit(im, size, Image.ANTIALIAS)

        thumb.save(os.path.join(item_storage, '{}_thumbnail{}'.format(file, ext)))

        return (file, ext)

    else:
        response = requests.get('https://s3.amazonaws.com/glancestore/{}'.format(filename), stream=True)
        # return Image.open(StringIO.StringIO(response.content))
        im = Image.open(io.BytesIO(response.content))
        file, ext = os.path.splitext(filename)
        # correct jpg naming to jpeg
        if ext == '.jpg':
            ext = '.jpeg'
        else:
            pass

        size = (200, 200)
        im.thumbnail(size, Image.ANTIALIAS)

        output = io.BytesIO()
        thumb = ImageOps.fit(im, size, Image.ANTIALIAS)

        thumb.save(output, ext[1:])
        output_file_name = '{}_thumbnail{}'.format(file, ext)

        # return (file, ext)
        return upload_to_s3_from_buffer(file_name=output_file_name, buffer=output)


def upload_to_s3_from_buffer(file_name, buffer):

    connection = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    bucket = connection.lookup(AWS_BUCKET)
    key = boto.s3.key.Key(bucket)
    key.name = file_name
    key.set_contents_from_string(buffer.getvalue(), headers={"Content-Type": "image/JPG"})
    url = key.generate_url(expires_in=0, query_auth=False)
    return url


def collect_Thumb(filename):
    """Opens image, makes thumbnail, saves to dir and returns filename plus
    extension in a tuple.
    Atti: filename takes the name of an image file.
    Bug:
    Eventually extend this to a func to include all image processing.
    """

    im = Image.open(os.path.join(item_storage, filename))

    file, ext = os.path.splitext(filename)
    size = (200, 200)

    thumb = ImageOps.fit(im, size, Image.ANTIALIAS)

    draw = ImageDraw.Draw(thumb)

    draw.line([(-20,50),(50,-20)], fill=(80, 170, 200), width=50)
    draw.line([(0,65),(65,0)], fill=(255, 255, 255), width=2)
    del draw

    thumb.save(os.path.join(item_storage, '{}_thumbnail{}'.format(file, ext)))

    return (file, ext)
