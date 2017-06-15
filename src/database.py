import time
import pathlib
import logging
# import json

import redis


logger = logging.getLogger('📚 ' + __name__)


class AbstractDB(object):
    def __len__(self):
        pass

    def __contains__(self, item: str or dict):
        pass

    def add(self, item: dict):
        pass

    def clear(self, period: int):
        pass


# deprecated in favor of RedisDB
class Database(AbstractDB):
    def __init__(self, path):
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

    def add(self, item: dict):
        post_id = item['id']
        datetime = item['datetime']
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
            logger.info('Creating NEW database...')
            with open(self._path, 'w'):
                pass
            return
        else:
            logger.info('Using OLD database...')

        with open(self._path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    item, t = line.split()
                    self._data[item] = float(t)


class RedisDB(AbstractDB):
    def __init__(self, redis_client: redis.StrictRedis):
        self.client = redis_client
        self._setup()

    def __len__(self):
        return len(self.client.hgetall('data'))

    def __contains__(self, item: str or dict):
        data = self.client.hgetall('data')
        if type(item) is str:
            item = item.encode('ascii')
            return item in data
        elif type(item) is dict:
            item = item['id'].encode('ascii')
            return item in data
        else:
            raise TypeError('Wrong item type')

    def add(self, item: dict):
        post_id = item['id']
        datetime = item['datetime']
        self.client.hset('data', post_id, datetime)
        self.client.sadd('dates', time.time())

    def clear(self, period: int):
        now = time.time()
        old_posts = set()

        for post_id, datetime in self.client.hgetall('data').items():
            datetime = int(datetime)
            if datetime + period < now:
                old_posts.add(post_id)

        for old_post_id in old_posts:
            self.client.hdel('data', old_post_id)

        return len(old_posts), len(self)

    def dates_list(self) -> list:
        return sorted(self.client.smembers('dates'))

    def _setup(self):
        version = self.client.get('version')
        new_version = time.time()
        if version:
            logger.info('Using OLD database')
            logger.info(f'Old version {version.decode("utf-8")}')
        else:
            logger.info('Using NEW database')
            # init_data = json.load(open('init.json'))
            # self.client.hmset('data', init_data)

        logger.info(f'New version: {new_version}')
        self.client.set('version', new_version)
