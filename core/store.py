import logging
from time import time
from typing import Dict

import redis

from core.decorators import log


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


class RedisStore(IdStore, SettingsStore):
    def __init__(self, prefix, url, clear_age):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.prefix = prefix
        self.clear_age = clear_age or 24 * 60 * 60

        if url:
            self.client = redis.Redis.from_url(url)
        else:
            self.client = redis.Redis()

        self.key_ids = self.prefix + ':ids'
        self.key_settings = self.prefix + ':settings'

    # ids
    @log
    def save_id(self, id):
        self.client.hset(self.key_ids, id, time())

    @log
    def has_id(self, id):
        return self.client.hexists(self.key_ids, id)

    @log
    def has_ids(self, ids: list):
        pipe = self.client.pipeline()
        for id in ids:
            pipe.hexists(self.key_ids, id)
        res = pipe.execute()
        return res

    @log
    def get_ids(self) -> Dict[str, int]:
        ids = self.client.hgetall(self.key_ids)
        return {id.decode('utf-8'): float(date) for id, date in ids.items()}

    @log
    def clear_ids(self):
        self.logger.info('Clearing database...')
        now = time()
        old_posts = []
        for post_id, datetime in self.client.hgetall(self.key_ids).items():
            if now - float(datetime) > self.clear_age:
                old_posts.append(post_id)
        if old_posts:
            self.client.hdel(self.key_ids, *old_posts)
        self.logger.info(f'Deleted: {len(old_posts)}.')

    # settings
    @log
    def set_setting(self, key, value):
        self.client.hset(self.key_settings, key, value)

    @log
    def get_setting(self, key):
        res = self.client.hget(self.key_settings, key)
        return res and res.decode('utf-8')

    @log
    def get_settings(self):
        sets = self.client.hgetall(self.key_settings)
        res = {}
        for key, value in sets.items():
            key, value = key.decode('utf-8'), value.decode('utf-8')
            res[key] = value
        return res
