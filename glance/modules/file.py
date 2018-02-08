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
import glance.config.settings


class UploadHandler():
    def __init__(self, account_session, filelist=None):
        self.account_session = account_session
        if filelist != None:
            if isinstance(filelist, list):
                self.filelist = filelist

            else:
                self.filelist = [filelist]

        else:
            self.filelist = filelist

        self.ALLOWED_FILE_TYPES = ['.jpg', '.zip', '.mp4']
        self.dst = glance.config.settings.tmp_upload
        self.salt = None


    def _to_dict(self, files):
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


    def _local_rename_file_with_salt(self, root, ext):
        if self.salt == None:
            self.salt = secrets.token_urlsafe(4)
            
        root = '{}_{}'.format(root, self.salt)

        return (root, ext)


    def _local_save_file(self, fileobj):
        root, ext = os.path.splitext(fileobj.filename)
        if ext not in self.ALLOWED_FILE_TYPES:
            # TODO: IMP error
            return False

        root, ext = self._local_rename_file_with_salt(root, ext)
        fileobj.save(os.path.join(self.dst, '{}{}'.format(root, ext)))

        return (root, ext)


    def _local_make_thumbnail(self, root, ext):
        if ext == '.jpg':
            thumbnail = image.thumb(self.dst, f'{root}{ext}')

        elif ext == '.mp4':
            saved_frame = image.save_frame(self.dst, f'{root}{ext}')
            thumbnail = image.thumb(self.dst, saved_frame)
            local_clean_up(self.dst, saved_frame)
        
        else:
            return False


        return (f'{root}{ext}', thumbnail)


    def _tags_from_string(self, string):
        return string.split(' ')


    def _taglist_append(self, taglist, tags_to_append):
        if len(taglist) != 0:
            for x in tags_to_append:
                taglist += ' ' + str(x)
        else:
            for x in tags_to_append:
                taglist += ' ' + str(x)

        return taglist


    @glance.app.celery.task
    def _local_clean_up(dst, filename):
        # TODO: remove dst from args
        os.remove(os.path.join(self.dst, filename))

        return filename
    

    def upload_collection_cover(self):
        try:
            root, ext = self._local_save_file(self.filelist[0])
        except:
            return False

        filename, thumbnail = self._local_make_thumbnail(root, ext)
        _local_file_to_s3.apply_async((dst, filename), link=local_clean_up.si(self.dst, filename))
        _local_file_to_s3.apply_async((dst, thumbnail), link=local_clean_up.si(self.dst, thumbnail))

        return (filename, thumbnail)


    def process_files(self, extra):
        payload = {'item_type': extra['itemradio']}
        res = glance.modules.api.post_item(self.account_session, payload)

        for file in self.filelist:
            root, ext = self._local_save_file(file)

            if ext == '.jpg' or ext == '.mp4':
                filename, thumbnail = self._local_make_thumbnail(root, ext)

                payload = {
                    'id': res[0]['id'], 
                    'name': root, 
                    'item_loc': filename, 
                    'item_thumb': thumbnail, 
                    'tags': glance.modules.api.tag_string(extra['tags'])
                }

                _local_file_to_s3.apply_async((self.dst, filename), link=[aws_rek_image.si(payload['id'], filename, self.account_session), local_clean_up.si(self.dst, filename)])
                _local_file_to_s3.apply_async((self.dst, thumbnail), link=local_clean_up.si(self.dst, thumbnail))

            if ext == '.zip':
                filename = f'{root}{ext}'
                _local_file_to_s3.apply_async((self.dst, filename), link=local_clean_up.si(self.dst, filename))

                payload['attached'] = filename

            res = glance.modules.api.put_item(self.account_session, payload)

        return res


    def upload_collection(self, flasksession, data):
        tags = self._taglist_append(data['tags'], self._tags_from_string(data['collection']))

        if 'items_for_collection' in data:
            payload = {
                'name': data['collection'],
                'item_type': 'collection',
                'item_loc': 'site/default_cover.jpg',
                'item_thumb': 'site/default_cover.jpg',
                'tags': tags,
                'items': ' '.join(data['items_for_collection']),
                'author': flasksession['username']
            }

            res = glance.modules.api.post_item(self.account_session, payload)

            return res

        else:
            payload = {
                'name': data['collection'],
                'item_type': 'collection',
                'item_loc': 'site/default_cover.jpg',
                'item_thumb': 'site/default_cover.jpg',
                'tags': data['tags'],
                'author': flasksession['username'],
            }

            res = glance.modules.api.post_item(self.account_session, payload)

            return res


@glance.app.celery.task
def _local_file_to_s3(dst, filename):
    # TODO: remove dst from args an
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
