from typing import List

from core.filter import BaseFilter
from core.store import IdStore
from .settings import ImgurSettings
from .models import Post
from .store import ImgurStore


# pre
class UniqueFilter(BaseFilter):
    def __init__(self, store: IdStore):
        super().__init__()
        self.store = store

    def filter(self, posts: list, *args, **kwargs):
        res = [post for post in posts if not self.store.has_id(post['id'])]
        self.logger.debug('> ' + str(len(posts)))
        self.logger.debug('< ' + str(len(res)))
        return res


class ScoreFilter(BaseFilter):
    def __init__(self, settings: ImgurSettings):
        super().__init__()
        self.settings = settings

    def filter(self, posts: list, *args, **kwargs):
        limit = self.settings.score
        res = [p for p in posts if int(p.get('score')) > limit]
        self.logger.debug('> ' + str(len(posts)))
        self.logger.debug('< ' + str(len(res)))
        return res


# post
class TagsFilter(BaseFilter):
    def __init__(self, store: ImgurStore):
        super().__init__()
        self.store = store

    def filter(self, posts: List[Post], *args, **kwargs):
        banned_tags = self.store.get_tags()
        has_tag = lambda p: p.tags in banned_tags
        has_word = lambda p: any(map(lambda b: b in p.title, banned_tags))

        res = [post for post in posts if not has_tag(post) and not has_word(post)]
        self.logger.debug('> ' + str(len(posts)))
        self.logger.debug('< ' + str(len(res)))
        return res


class SizeFilter(BaseFilter):
    def __init__(self, settings: ImgurSettings):
        super().__init__()
        self.settings = settings

    def filter(self, posts: List[Post], *args, **kwargs):
        res = []
        for p in posts:
            limit = max(self.settings.post_len, self.settings.long_post_len)
            if all(map(lambda i: i.height / i.width < self.settings.max_dim,
                       p.images[:limit])):
                res.append(p)
        self.logger.debug('> ' + str(len(posts)))
        self.logger.debug('< ' + str(len(res)))
        return posts
