from typing import List

from telegram_autoposter.filters import Filter

from .models import Post
from .store import Store


class ScoreFilter(Filter):
    def filter(self, posts: List[Post], limit=0, *args, **kwargs) -> List[Post]:
        self.logger.debug('Filtering...')
        return [post for post in posts if post.score > limit]


class UniqueFilter(Filter):
    def filter(self, posts: List[Post], store: Store, *args, **kwargs):
        self.logger.debug('Filtering...')
        return [post for post in posts if not store.has_id(post.id)]
