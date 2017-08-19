from telegram_autoposter.pipes import Pipe

from telegram.ext import Updater

from settings import reddit_settings
from .fetcher import RedditFetcher
from .filters import ScoreFilter, UniqueFilter
from .modeller import RedditModeller
from .poster import RedditPoster
from .store import Store


class RedditPipe(Pipe):
    post_interval = 30
    modeller_class = RedditModeller
    poster_class = RedditPoster

    def __init__(self, channel_id: str, updater: Updater, store: Store):
        super().__init__(channel_id, updater)
        self.store = store
        self.limits = []

    def pre_schedule_hook(self):
        self.post_interval = int(self.store.get_setting('post_interval'))
        self.scheduler.add_job(self.store.clear, reddit_settings['db_clear_interval'])

    def pre_post_hook(self):
        self.set_limits()

    def set_limits(self):
        self.limits = []
        limits = self.store.get()  # { subreddit_name: score_limit }
        for name, score in limits.items():
            self.limits.append((name, score))

    def fetch_data(self):
        subreddits = []
        fetcher = RedditFetcher()
        for name, score in self.limits:
            subreddits.append(fetcher.fetch(name))
        return subreddits

    def filter_data(self, subreddits):
        score_filter = ScoreFilter()
        unique_filter = UniqueFilter()

        posts = []
        self.logger.debug(f'posts size: {sum([len(s) for s in subreddits])}')

        for i, subreddit in enumerate(subreddits):
            filtered = score_filter.filter(subreddit, self.limits[i][1])
            posts.extend(filtered)
        self.logger.debug(f'posts size: {len(posts)}')

        posts = unique_filter.filter(posts, self.store)
        self.logger.debug(f'posts size: {len(posts)}')
        return posts

    def post_data(self, data):
        poster = RedditPoster(self.channel_id, self.updater, self.store)
        poster.post(data)
