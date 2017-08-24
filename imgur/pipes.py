from core.pipe import BasePipe

from telegram.ext import Updater

from .fetchers import GalleryFetcher
from .filters import UniqueFilter, SizeFilter, TagsFilter
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

    def set_up(self, channel_id: str, updater: Updater, store: ImgurStore, settings: ImgurSettings):
        super(ImgurPipe, self).set_up(channel_id, updater)
        self.store = store
        self.settings = settings

    def pre_cycle_hook(self):
        self.post_interval = self.settings.post_interval
        self.scheduler.run_repeating(self.store.clear_ids, interval=2 * 24 * 60 * 60, first=0)

    def get_pre_filters(self):
        return [UniqueFilter(self.store)]

    def get_modeller(self):
        return ImgurModeller(self.settings)

    def get_post_filters(self):
        return [TagsFilter(self.store), SizeFilter()]

    def get_publisher(self):
        return ImgurPublisher(self.channel_id, self.updater, self.store)
