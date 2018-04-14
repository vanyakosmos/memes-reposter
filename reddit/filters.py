import re
from typing import List

from core.filter import BaseFilter
from core.store import IdStore
from .models import Post
from .store import RedditStore


# before modelling
class UniqueFilter(BaseFilter):
    def __init__(self, store: IdStore):
        super().__init__()
        self.store = store

    def filter(self, subreddits: List[List[dict]], *args, **kwargs):
        filtered_subs = []
        for posts in subreddits:
            ids = [post['data']['id'] for post in posts]
            posted = self.store.has_ids(ids)
            posts = [posts[i] for i in range(len(ids)) if not posted[i]]
            filtered_subs.append(posts)

        self.logger.debug(f'> {sum([len(s) for s in subreddits])}')
        self.logger.debug(f'< {sum([len(s) for s in filtered_subs])}')
        return filtered_subs


# after modelling
class ScoreFilter(BaseFilter):
    def __init__(self, limits):
        super().__init__()
        self.limits = limits

    def filter(self, subreddits: List[List[Post]], *args, **kwargs) -> List[Post]:
        posts = []
        for i, subreddit in enumerate(subreddits):
            filtered = [post for post in subreddit if post.score > self.limits[i][1]]
            posts.extend(filtered)

        self.logger.debug(f'> {sum([len(s) for s in subreddits])}')
        self.logger.debug(f'< {len(posts)}')
        return posts


class UniqueUrlFilter(BaseFilter):
    def __init__(self, store: RedditStore):
        super().__init__()
        self.store = store

    def filter(self, posts: List[Post], *args, **kwargs):
        urls = [post.url for post in posts]
        posted = self.store.has_urls(urls)
        filtered_posts = [
            post
            for post, was_posted in zip(posts, posted)
            if not was_posted
        ]
        self.logger.debug(f'> {len(posts)}')
        self.logger.debug(f'< {len(filtered_posts)}')
        return filtered_posts


class NSFWFilter(BaseFilter):
    def filter(self, posts: List[Post], *args, **kwargs) -> List[Post]:
        filtered_posts = [p for p in posts if not p.nsfw]
        self.logger.debug(f'> {len(posts)}')
        self.logger.debug(f'< {len(filtered_posts)}')
        return filtered_posts


class BullshitFilter(BaseFilter):
    # todo: store bs words in DB
    bullshit = {
        'meet', 'surgeries', 'surgery', 'war', 'donated', 'donate',
        'reddit', 'adopted', 'adopt', 'chemotherapy', 'cancer',
        'medical', 'pounds', 'baby', 'toddler', 'wedding', 'bride',
        'rescue', 'rescued', 'adopting', 'adopted', 'citizenship', 'citizen',
    }

    def contains_bs(self, title: str):
        title = re.sub(r'[^\s\w]+', ' ', title)
        words = title.lower().split()
        return any([word in self.bullshit for word in words])

    def filter(self, posts: List[Post], *args, **kwargs) -> List[Post]:
        filtered_posts = [p for p in posts if not self.contains_bs(p.title)]
        self.logger.debug(f'> {len(posts)}')
        self.logger.debug(f'< {len(filtered_posts)}')
        return filtered_posts
