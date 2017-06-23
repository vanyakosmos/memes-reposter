import logging

from telegram import Bot
from telegram.ext import Updater, Dispatcher

from autoposter import AbstractDB, Scheduler, Collector


class ChannelSetup(object):
    def __init__(self, channel_name: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.channel_name = channel_name
        self.bot: Bot = None
        self.updater: Updater = None
        self.dispatcher: Dispatcher = None
        self.collector: Collector = None
        self.database: AbstractDB = None
        self.scheduler: Scheduler = None
        self.handlers = []

    @property
    def name(self):
        return self.channel_name

    def setup_dependencies(self, bot: Bot, updater: Updater, dispatcher: Dispatcher):
        self.logger.debug('Setup dependencies.')
        self.bot = bot
        self.updater = updater
        self.dispatcher = dispatcher
        self.database = self.get_database()
        self.scheduler = self.get_scheduler()

    def start(self):
        self.scheduler.run()

    def add_commands_handlers(self):
        """
        Add command handlers if this channel was chosen.
        """
        self.logger.debug('Adding commands handlers.')
        for handler in self.handlers:
            self.dispatcher.add_handler(handler)

    def remove_command_handlers(self):
        """
        Remove command handlers if another channel was chosen.
        """
        self.logger.debug('Removing commands handlers.')
        for handler in self.handlers:
            self.dispatcher.remove_handler(handler)

    def get_database(self) -> AbstractDB:
        pass

    def get_scheduler(self) -> Scheduler:
        pass

    def help_text(self) -> str:
        """
        Text that will appear after choosing channel.
        """
        pass
