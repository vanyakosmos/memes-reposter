import logging

from telegram.ext import Updater


class BasePublisher(object):
    def __init__(self, channel_id: str, updater: Updater):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.channel_id = channel_id
        self.bot = updater.bot

    def publish(self, post, *args, **kwargs):
        self.logger.debug('Posting... (actually not)')
        self.logger.debug(post)
