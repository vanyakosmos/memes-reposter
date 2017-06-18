import pathlib
import time

import redis

from autoposter import AbstractDB


# deprecated in favor of RedisDB
class Database(AbstractDB):
    def __init__(self, path):
        super().__init__()
        self._data = {}
        self._path = path
        self._setup()

    def __len__(self):
        return len(self._data)

    def __contains__(self, item: str or dict):
        if type(item) is str:
            return item in self._data
        elif type(item) is dict:
            return item['id'] in self._data
        else:
            raise TypeError('Wrong item type')

    def add(self, post_id, datetime):
        if post_id not in self:
            self._data[post_id] = datetime
            with open(self._path, 'a') as file:
                file.write(f'{post_id} {datetime}\n')

    def clear(self, period: int):
        now = time.time()

        old_posts = set()
        for post_id, datetime in self._data.items():
            if datetime + period < now:
                old_posts.add(post_id)

        for old_post in old_posts:
            del self._data[old_post]

        with open(self._path, 'w') as file:
            for post_id, datetime in self._data.items():
                file.write(f'{post_id} {datetime}\n')
        return len(old_posts), len(self._data)

    def _setup(self):
        path = pathlib.Path(self._path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            self.logger.info('Creating NEW database...')
            with open(self._path, 'w'):
                pass
            return
        else:
            self.logger.info('Using OLD database...')

        with open(self._path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    item, t = line.split()
                    self._data[item] = float(t)


class RedisDB(AbstractDB):
    def __init__(self, name: str, redis_client: redis.StrictRedis):
        super().__init__()
        self.client = redis_client
        self.name = name
        self.data = name + ':data'
        self.dates_name = name + ':dates'
        self._check()

    def __len__(self):
        return self.client.hlen(self.data)

    def __contains__(self, post_id: str):
        return self.client.hexists(self.data, post_id)

    def add(self, post_id, datetime):
        self.client.hset(self.data, post_id, datetime)
        self.client.sadd(self.dates_name, time.time())

    # todo: make transaction with pipe
    def clear(self, period: int):
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

        return len(old_posts), len(self)

    def dates_list(self) -> list:
        return sorted(self.client.smembers(self.dates_name))

    def _check(self):
        if self.client.exists(self.data):
            self.logger.info(self.name + ': Using OLD database')
        else:
            self.logger.info(self.name + ': Using NEW database')
