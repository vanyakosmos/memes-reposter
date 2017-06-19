import logging


class Collector(object):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)

    def collect(self):
        raise NotImplementedError

    def publish(self):
        raise NotImplementedError

    @property
    def size(self):
        raise NotImplementedError

    @property
    def is_empty(self) -> bool:
        return self.size == 0


