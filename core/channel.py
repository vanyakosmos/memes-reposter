import logging
from typing import List

from telegram.ext import Updater

from core.pipe import BasePipe


class BaseChannel(object):
    def __init__(self):
        """
        - name: name of channel in telegram. **Must** starts with "@".
        - label: identifier for channel. **Must** be unique.
        - pipe_classes:
        - commands_handlers: list of command handlers which would be attached when we need them and detached when we don't.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.label = self.__class__.__name__
        self.channel_id = self.get_channel_id()
        self.pipes: List[BasePipe] = []
        self.updater = None
        self.dispatcher = None
        self.commands_handlers = []

    def get_channel_id(self):
        raise NotImplementedError('Specify channel id. Name must be started with "@".')

    def set_up(self, updater: Updater):
        self.updater = updater
        self.dispatcher = updater.dispatcher

    def start(self):
        """
        Schedule posting for each pipe.
        """
        for pipe in self.pipes:
            pipe.set_up(self.channel_id, self.updater)
            pipe.start_posting_cycle()

    def add_commands_handlers(self):
        """
        Used by manager class when changing channel command namespace.
        """
        for handler in self.commands_handlers:
            self.dispatcher.add_handler(handler)

    def remove_commands_handlers(self):
        """
        Used by manager class when changing channel command namespace.
        """
        for handler in self.commands_handlers:
            self.dispatcher.remove_handler(handler)

    def help_text(self):
        """
        Used by manager class to print out info about commands specified for channel.
        """
        pass
