import logging
from typing import List

from telegram.ext import Updater

from core.fetcher import BaseFetcher
from core.filter import BaseFilter
from core.modeller import BaseModeller
from core.publisher import BasePublisher
from core.scheduler import Scheduler
from core.decorators import log


class BasePipe(object):
    fetcher_class = BaseFetcher
    modeller_class = BaseModeller
    publisher_class = BasePublisher

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.post_interval = 10 * 60
        self.channel_id = None
        self.updater = None
        self.scheduler = None

    @log
    def set_up(self, channel_id: str, updater: Updater):
        self.channel_id = channel_id
        self.updater = updater
        self.scheduler = Scheduler(self.updater.job_queue)

    @log
    def start_posting_cycle(self):
        self.pre_cycle_hook()
        self.scheduler.run_once(self._fetch, 0)

    @log
    def pre_cycle_hook(self):
        pass

    # fetch
    @log
    def _fetch(self):
        self.pre_fetch_hook()
        data = self.fetch()
        self._pre_model_filter(data)

    @log
    def fetch(self):
        fetcher = self.get_fetcher()
        return fetcher.fetch()

    @log
    def get_fetcher(self) -> BaseFetcher:
        return self.fetcher_class()

    @log
    def pre_fetch_hook(self):
        pass

    # pre model filter
    @log
    def _pre_model_filter(self, data):
        data = self.pre_model_filter(data)
        self._model(data)

    @log
    def pre_model_filter(self, data):
        filters = self.get_pre_filters()
        for flr in filters:
            data = flr.filter(data)
        return data

    @log
    def get_pre_filters(self) -> List[BaseFilter]:
        return []

    # model
    @log
    def _model(self, data):
        posts = self.model(data)
        self._post_model_filter(posts)

    @log
    def model(self, data):
        modeller = self.get_modeller()
        return modeller.model(data)

    @log
    def get_modeller(self) -> BaseModeller:
        return self.modeller_class()

    # post model filter
    @log
    def _post_model_filter(self, posts):
        posts = self.post_model_filter(posts)
        self._publish(posts)

    @log
    def post_model_filter(self, posts):
        filters = self.get_post_filters()
        for flr in filters:
            posts = flr.filter(posts)
        return posts

    @log
    def get_post_filters(self) -> List[BaseFilter]:
        return []

    # publish
    @log
    def _publish(self, posts):
        publisher = self.get_publisher()
        self.scheduler.run_once(self.schedule_posts, 0, None, publisher, posts)

    @log
    def get_publisher(self) -> BasePublisher:
        return self.publisher_class(self.channel_id, self.updater)

    @log
    def schedule_posts(self, publisher: BasePublisher, posts: list):
        """
        Recursively post item and schedule posting for next one.
        After posting everything schedule new fetch-model-filter-post cycle.
        :param publisher:
        :param posts:
        """
        if posts:
            head, *tail = posts
            publisher.publish(head)
            self.scheduler.run_once(self.schedule_posts, 0, None, publisher, tail)
        else:
            self.logger.info('Finished posting.')
            self.scheduler.run_once(self.start_posting_cycle, self.post_interval)
