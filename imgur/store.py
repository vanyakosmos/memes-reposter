from typing import List

from core import store


class ImgurStore(store.RedisStore):
    def __init__(self, prefix, url, clear_age):
        super().__init__(prefix, url, clear_age)
        self.key_tags = prefix + ':tags'

    # banned tags
    def get_tags(self):
        tags = self.client.smembers(self.key_tags)
        if tags:
            return [tag.decode('utf-8') for tag in tags]
        else:
            return []

    def add_tags(self, tags: List[str]):
        if tags:
            self.client.sadd(self.key_tags, *[tag.lower() for tag in tags])

    def remove_tags(self, tags: List[str]):
        if tags:
            self.client.srem(self.key_tags, *[tag.lower() for tag in tags])
