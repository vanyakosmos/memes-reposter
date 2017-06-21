import logging

from telegram import Bot

from autoposter import AbstractDB


class Collector(object):
    def __init__(self, bot: Bot, db: AbstractDB):
        self.bot = bot
        self.db = db
        self._updated = False
        self.logger = logging.getLogger(self.__class__.__name__)

    def collect(self):
        self._updated = False

    def publish(self):
        raise NotImplementedError

    @property
    def size(self):
        raise NotImplementedError

    @property
    def is_empty(self) -> bool:
        return self.size == 0

    def was_updates(self):
        return self._updated


