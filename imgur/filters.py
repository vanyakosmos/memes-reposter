from typing import List

from core.filter import BaseFilter

from core.store import IdStore
from .models import Post
from .store import ImgurStore


class UniqueFilter(BaseFilter):
    def __init__(self, store: IdStore):
        super().__init__()
        self.store = store

    def filter(self, posts: list, *args, **kwargs):
        self.logger.debug('Was: ' + str(len(posts)))
        res = [post for post in posts if not self.store.has_id(post['id'])]
        self.logger.debug('Now: ' + str(len(res)))
        return res


class TagsFilter(BaseFilter):
    def __init__(self, store: ImgurStore):
        super().__init__()
        self.store = store

    def filter(self, posts: List[Post], *args, **kwargs):
        self.logger.debug('Was: ' + str(len(posts)))
        banned_tags = self.store.get_tags()
        res = [post for post in posts if post.tags not in banned_tags]
        self.logger.debug('Now: ' + str(len(res)))
        return res


class SizeFilter(BaseFilter):
    def filter(self, posts: List[Post], *args, **kwargs):
        self.logger.debug('Filtering...')
        return posts
