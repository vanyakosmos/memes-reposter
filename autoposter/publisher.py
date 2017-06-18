import logging

from telegram import Bot

from .database import AbstractDB


class AbstractPublisher(object):
    def __init__(self, bot: Bot, db: AbstractDB, channel_id: str):
        self.bot = bot
        self.db = db

        self.channel_id = channel_id
        self.logger = logging.getLogger(self.__class__.__name__)

    def publish(self, data):
        pass
