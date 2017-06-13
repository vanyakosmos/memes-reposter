import time
import pathlib


class Database(object):
    def __init__(self, path):
        self._data = {}
        self._path = path
        self._restore_database()

    def __contains__(self, item):
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

    def clear(self):
        period = 10 * 24 * 60 * 60  # 10 days
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

    def _restore_database(self):
        path = pathlib.Path(self._path)
        if not path.exists():
            with open(self._path, 'w+'):
                pass
            return

        with open(self._path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    item, t = line.split()
                    self._data[item] = float(t)
