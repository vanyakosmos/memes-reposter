import time
from typing import Set

import redis

from autoposter import AbstractDB


class RedisDB(AbstractDB):
    def __init__(self, name: str, redis_client: redis.StrictRedis):
        super().__init__()
        self.client = redis_client
        self.name = name
        self.data = name + ':data'
        self.dates_name = name + ':dates'
        self._check()

    def add(self, post_id, datetime):
        self.client.hset(self.data, post_id, datetime)
        self.client.sadd(self.dates_name, time.time())

    def keys(self) -> Set[str]:
        return {key.decode('utf-8') for key in self.client.hkeys(self.data)}

    def clear(self, period: int) -> (int, int):
        now = time.time()

        # remove old posts from hash `data`
        old_posts = []
        for post_id, datetime in self.client.hgetall(self.data).items():
            if float(datetime) + period < now:
                old_posts.append(post_id)
        if old_posts:
            self.client.hdel(self.data, *old_posts)

        # remove old date marks from set `dates`
        old_date_marks = []
        for date_mark in self.client.smembers(self.dates_name):
            if float(date_mark) + period < now:
                old_date_marks.append(date_mark)
        if old_date_marks:
            self.client.srem(self.dates_name, *old_date_marks)

        return len(old_posts), self.client.hlen(self.data)

    def dates_list(self) -> list:
        return sorted(self.client.smembers(self.dates_name))

    def _check(self):
        if self.client.exists(self.data):
            self.logger.info(self.name + ': Using OLD database')
        else:
            self.logger.info(self.name + ': Using NEW database')
