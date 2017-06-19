import random
from typing import List

from autoposter.collector import Collector
from settings import TELEMGUR_CHANNEL_ID, SUBREDDIT_CHANNEL_ID

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
    def __init__(self, bot, db):
        super().__init__(bot, db)
        self.posts: List[Post] = []

        self.fetcher = SubredditFetcher()
        self.pics_publisher = SubredditPublisher(bot=self.bot, db=self.db,
                                                 channel_id=SUBREDDIT_CHANNEL_ID)

        self.filters = {}
        self.subreddits = {}
        for subreddit, score in [('funny', 5000), ('pics', 5000), ('gifs', 5000), ('aww', 5000)]:
            self.add_subreddit(subreddit, score=score)

    def add_subreddit(self, subreddit: str, score: int):
        self.subreddits[subreddit] = score
        self.filters[subreddit] = SubredditFilter(db=self.db, subreddit=subreddit, score=score)

    def remove_subreddit(self, subreddit):
        del self.subreddits[subreddit]
        del self.filters[subreddit]

    def get_subreddits(self) -> dict:
        return dict(self.subreddits)

    def collect(self):
        """
        Fetch and filter posts. Store them is ``sell.posts``.
        """
        for subreddit in self.filters:
            response = self.fetcher.fetch(subreddit)
            if not response.success:
                continue
            if not response.data:
                continue

            posts = self.filters[subreddit].filter(response.data)
            self.posts.extend(posts)
            self.logger.info(f'Subreddit: {subreddit} ~ Received {len(posts)}')

    def publish(self):
        """
        Publish ONE post into telegram and remove it from ``self.posts`` list.
        """
        index = random.randint(0, self.size - 1)
        post = self.posts.pop(index)
        self.pics_publisher.publish(post)

    @property
    def size(self):
        return len(self.posts)
