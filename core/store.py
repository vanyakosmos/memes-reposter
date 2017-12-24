import logging
from time import time
from typing import Dict

import pymongo

from core.decorators import log


logger = logging.getLogger(__name__)


class IdStore(object):
    def save_id(self, id):
        raise NotImplementedError

    def has_id(self, id):
        raise NotImplementedError

    def has_ids(self, ids: list):
        raise NotImplementedError

    def clear_ids(self):
        raise NotImplementedError

    def get_ids(self):
        raise NotImplementedError


class SettingsStore(object):
    def set_setting(self, key, value):
        raise NotImplementedError

    def get_settings(self):
        raise NotImplementedError


class MongoStore(IdStore, SettingsStore):
    def __init__(self, name: str, url: str, clear_age: int):
        self.name = name
        self.clear_age = clear_age or 24 * 60 * 60

        self.client = pymongo.MongoClient(url)
        self.db = self.client.get_database()

        self.posts = self.get_collection('posts')
        self.settings = self.get_collection('settings')
        self.fset = self.get_settings_instance_filter()

    def get_collection(self, name: str):
        return self.db.get_collection('_'.join([self.name, name]))

    def get_settings_instance_filter(self):
        s = self.settings.find_one({}, {'_id': 1})
        if s is None:
            s = self.settings.insert_one({})
            s = {'_id': s.inserted_id}
        return s

    # ids
    @log
    def save_id(self, id):
        self.posts.insert_one({'id': id, 'timestamp': time()})

    @log
    def has_id(self, id):
        post = self.posts.find_one({'id': id})
        return post is not None

    @log
    def has_ids(self, ids: list):
        posts = self.posts.find({})
        posts_ids = {p['id'] for p in posts}
        res = [
            id in posts_ids
            for id in ids
        ]
        return res

    @log
    def get_ids(self) -> Dict[str, int]:
        posts = self.posts.find()
        res = {
            p['id']: p['timestamp']
            for p in posts
        }
        return res

    @log
    def clear_ids(self):
        logger.info('Clearing database...')
        now = time()
        res = self.posts.delete_many({
            'timestamp': {
                '$lt': now - self.clear_age
            }
        })
        logger.info(f'Deleted: {res.deleted_count}.')

    # settings
    @log
    def set_setting(self, key, value):
        self.settings.update(self.fset, {
            '$set': {key: value}
        })

    @log
    def get_setting(self, key):
        s: dict = self.settings.find_one(self.fset)
        return s.get(key, None)

    @log
    def get_settings(self):
        s: dict = self.settings.find_one(self.fset, {'_id': 0})
        return s
