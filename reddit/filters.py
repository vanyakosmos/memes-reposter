from typing import List

from core.filter import BaseFilter
from core.store import IdStore
from .models import Post


class ScoreFilter(BaseFilter):
    def __init__(self, limits):
        super().__init__()
        self.limits = limits

    def filter(self, subreddits: List[List[Post]], *args, **kwargs) -> List[Post]:
        self.logger.debug(f'Was: {sum([len(s) for s in subreddits])}')
        posts = []

        for i, subreddit in enumerate(subreddits):
            filtered = [post for post in subreddit if post.score > self.limits[i][1]]
            posts.extend(filtered)
        self.logger.debug(f'Now: {len(posts)}')
        return posts


class UniqueFilter(BaseFilter):
    def __init__(self, store: IdStore):
        super().__init__()
        self.store = store

    def filter(self, subreddits: List[List[dict]], *args, **kwargs):
        self.logger.debug(f'Was: {sum([len(s) for s in subreddits])}')
        filtered_subs = []

        for posts in subreddits:
            posts = [post for post in posts if not self.store.has_id(post['data']['id'])]
            filtered_subs.append(posts)
        self.logger.debug(f'Now: {sum([len(s) for s in filtered_subs])}')
        return filtered_subs
