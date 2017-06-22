import random
from typing import List, Dict

from autoposter.collector import Collector
from settings import TELEMGUR_CHANNEL_ID, SUBREDDIT_CHANNEL_ID
from src.database import RedditRedisDB

from .fetcher import GalleryFetcher, SubredditFetcher
from .filter import PostsFilter, SubredditFilter
from .publisher import ImgurPostPublisher, SubredditPublisher
from .wrappers import Post


class ImgurCollector(Collector):
    def __init__(self, bot, db):
        super().__init__(bot, db)
        self.posts = []

        self.fetcher = GalleryFetcher()
        self.filter = PostsFilter(db=self.db)
        self.publisher = ImgurPostPublisher(bot=self.bot, db=self.db,
                                            channel_id=TELEMGUR_CHANNEL_ID)

    def collect(self):
        """
        Fetch and filter posts. Store them is ``sell.posts``.
        """
        super().collect()
        data = []
        response = self.fetcher.fetch()
        if response.success:
            data.extend(response.data)

        if self.filter:
            self.posts = self.filter.filter(data)
        else:
            self.posts = data

    def publish(self):
        """
        Publish ONE post into telegram and remove it from ``self.posts`` list.
        """
        post = self.posts.pop(0)
        self.publisher.publish(post)

    @property
    def size(self):
        return len(self.posts)


class RedditCollector(Collector):
    def __init__(self, bot, db: RedditRedisDB, subreddits_scores):
        super().__init__(bot, db)
        self.posts: List[Post] = []

        self.fetcher = SubredditFetcher()
        self.pics_publisher = SubredditPublisher(bot=self.bot, db=self.db,
                                                 channel_id=SUBREDDIT_CHANNEL_ID)

        self.filters = {}
        self.subreddits = {}
        self.add_subreddits(subreddits_scores)

    def add_subreddits(self, subreddits: Dict[str, int]):
        self._updated = True
        for subreddit, score in subreddits.items():
            if subreddit in self.subreddits:
                self.logger.info(f'Updating subreddit "{subreddit}" with new score limit {score}.')
            else:
                self.logger.info(f'Adding subreddit "{subreddit}" with score limit {score}.')
            self.subreddits[subreddit] = score
            self.filters[subreddit] = SubredditFilter(db=self.db, subreddit=subreddit, score=score)
        self.db.add_subreddits(subreddits)

    def remove_subreddits(self, subreddits: List[str]) -> List[str]:
        removed = []
        for subreddit in subreddits:
            if subreddit in self.subreddits:
                self.logger.info(f'Removing subreddit "{subreddit}".')
                del self.subreddits[subreddit]
                del self.filters[subreddit]
                removed.append(subreddit)
        self.db.remove_subreddits(subreddits)
        if removed:
            self._updated = True
        return removed

    def get_subreddits(self) -> dict:
        return dict(self.subreddits)

    def collect(self):
        """
        Fetch and filter posts. Store them is ``sell.posts``.
        """
        super().collect()
        self.posts = []  # in case if collector was marked as updated and scheduler rerun collect() b4 post all posts
        for subreddit in self.filters:
            response = self.fetcher.fetch(subreddit)
            if not response.success:
                continue
            if not response.data:
                continue

            posts = self.filters[subreddit].filter(response.data)
            self.posts.extend(posts)
            self.logger.info(f'Subreddit: {subreddit:15s} ~ Received {len(posts)}')

    def publish(self):
        """
        Publish ONE post into telegram and remove it from ``self.posts`` list.
        """
        index = random.randrange(self.size)
        post = self.posts.pop(index)
        self.pics_publisher.publish(post)

    @property
    def size(self):
        return len(self.posts)
