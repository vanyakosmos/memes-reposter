from typing import List

from core.filter import BaseFilter
from core.store import IdStore
from .settings import ImgurSettings
from .models import Post


# pre
class UniqueFilter(BaseFilter):
    def __init__(self, store: IdStore):
        super().__init__()
        self.store = store

    def filter(self, posts: list, *args, **kwargs):
        ids = [p['id'] for p in posts]
        posted = self.store.has_ids(ids)
        res = [posts[i] for i in range(len(ids)) if not posted[i]]

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
    def __init__(self, banned_tags: set):
        super().__init__()
        self.banned_tags = banned_tags

    def has_tag(self, p: Post):
        return any(map(lambda b: b in self.banned_tags, p.tags))

    def has_word(self, p: Post):
        title_words = set(p.title.lower().split())
        return any(map(lambda b: b in title_words, self.banned_tags))

    def filter(self, posts: List[Post], *args, **kwargs):
        res = [post for post in posts
               if not self.has_tag(post)
               and not self.has_word(post)]
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
