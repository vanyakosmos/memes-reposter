from typing import List

from pymongo.errors import DuplicateKeyError

from core2 import store


class ImgurStore(store.MongoStore):
    def __init__(self, name, url, clear_age):
        super().__init__(name, url, clear_age)
        self.tags = self.get_collection('tags')
        self.tags.create_index('name', unique=True)

    def get_tags(self) -> set:
        tags = self.tags.find()
        tags = {t['name'] for t in tags}
        return tags

    def add_tags(self, tags: List[str]):
        for t in tags:
            try:
                self.tags.insert_one({
                    'name': t
                })
            except DuplicateKeyError:
                pass

    def remove_tags(self, tags: List[str]):
        self.tags.delete_many({
            'name': {
                '$in': tags
            }
        })
