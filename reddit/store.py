import logging
from typing import List, Dict
from time import time

import redis


class Store(object):
    clear_age = 2 * 24 * 60 * 60

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def save_id(self, id):
        pass

    def has_id(self, id) -> bool:
        pass

    def get(self) -> Dict[str, int]:
        pass

    def add(self, subreddits: Dict[str, int]):
        pass

    def remove(self, subreddits: List[str]):
        pass

    def clear(self):
        pass

    def set_up_settings(self, settings):
        pass

    def get_setting(self, param):
        pass

    def change_setting(self, key, value):
        pass


class InMemoryStore(Store):
    def __init__(self):
        super().__init__()
        self.ids = {}
        self.subreddits = {
            'funny': 5000,
            'gifs': 5000,
        }

    def save_id(self, id):
        self.ids[id] = time()

    def has_id(self, id) -> bool:
        return id in self.ids

    def get(self) -> Dict[str, int]:
        return self.subreddits

    def add(self, subreddits: Dict[str, int]):
        for name, score in subreddits.items():
            self.subreddits[name] = score

    def remove(self, subreddits: List[str]):
        removed = []
        for name in subreddits:
            if name in self.subreddits:
                del self.subreddits[name]
                removed.append(name)
        return removed

    def clear(self):
        self.logger.info('Clearing database...')
        now = time()
        new_ids = {}
        for id, date in self.ids.items():
            if now - date < self.clear_age:
                new_ids[id] = date
        self.ids = new_ids


class RedisStore(Store):
    def __init__(self, prefix, url=None, clear_age=None):
        super().__init__()
        # self.prefix = prefix
        if url:
            self.client = redis.Redis.from_url(url)
        else:
            self.client = redis.Redis()
        self.key_ids = prefix + ':ids'
        self.key_subreddits = prefix + ':subreddits'
        self.key_settings = prefix + ':settings'
        if clear_age:
            self.clear_age = clear_age

    def set_up_settings(self, post_interval):
        self.client.hsetnx(self.key_settings, 'post_interval', post_interval)

    def get_setting(self, key):
        res = self.client.hget(self.key_settings, key)
        if res:
            return res.decode('utf-8')
        return None

    def change_setting(self, key, value):
        if self.client.hexists(self.key_settings, key):
            self.client.hset(self.key_settings, key, value)
            return True
        else:
            return False

    def save_id(self, id):
        self.client.hset(self.key_ids, id, time())

    def has_id(self, id):
        return self.client.hexists(self.key_ids, id)

    def get(self) -> Dict[str, int]:
        res = self.client.hgetall(self.key_subreddits)
        subreddits = {}
        for name, score in res.items():
            subreddits[name.decode('utf-8')] = int(score)
        return subreddits

    def add(self, subreddits: Dict[str, int]):
        self.client.hmset(self.key_subreddits, subreddits)

    def remove(self, subreddits: List[str]):
        self.client.hdel(self.key_subreddits, *subreddits)

    def clear(self):
        self.logger.info('Clearing database...')
        now = time()
        old_posts = []
        for post_id, datetime in self.client.hgetall(self.key_ids).items():
            if now - float(datetime) > self.clear_age:
                old_posts.append(post_id)
        if old_posts:
            self.client.hdel(self.key_ids, *old_posts)
