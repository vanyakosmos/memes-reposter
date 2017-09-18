from telegram.ext import Updater

from settings import CLEAR_INTERVAL
from core.pipe import BasePipe
from core.decorators import log
from .fetchers import GalleryFetcher
from .filters import UniqueFilter, SizeFilter, TagsFilter, ScoreFilter
from .modeller import ImgurModeller
from .publisher import ImgurPublisher
from .store import ImgurStore
from .settings import ImgurSettings


class ImgurPipe(BasePipe):
    fetcher_class = GalleryFetcher

    def __init__(self):
        super().__init__()
        self.store = None
        self.settings = None
        self.post_interval = 10 * 60

    def set_up(self, channel_id: str, updater: Updater, **kwargs):
        store: ImgurStore = kwargs['store']
        settings: ImgurSettings = kwargs['settings']
        super(ImgurPipe, self).set_up(channel_id, updater)
        self.store = store
        self.settings = settings

    @log
    def pre_cycle_hook(self):
        self.post_interval = self.settings.post_interval
        self.scheduler.run_repeating(self.store.clear_ids, interval=CLEAR_INTERVAL, first=0)

    @log
    def get_pre_filters(self):
        return [UniqueFilter(self.store), ScoreFilter(self.settings), ]

    @log
    def get_modeller(self):
        return ImgurModeller(self.settings)

    @log
    def get_post_filters(self):
        tags = self.store.get_tags()
        return [TagsFilter(tags), SizeFilter(self.settings), ]

    @log
    def get_publisher(self):
        return ImgurPublisher(self.channel_id, self.updater, self.store)
