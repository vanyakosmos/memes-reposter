import logging
from typing import List

from telegram import Message
from telegram.ext import Updater, BaseFilter, CommandHandler

from core.pipe import BasePipe
from core.decorators import log


class ActiveUsersFilter(BaseFilter):
    def __init__(self, active_users):
        self.active_users = active_users

    def filter(self, message: Message):
        return message.from_user.id in self.active_users


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
        self.pipes = self.get_pipes()
        self.updater = None
        self.dispatcher = None
        self.active_users = set()

    def get_channel_id(self):
        raise NotImplementedError('Specify channel id. Name must be started with "@".')

    def get_pipes(self) -> List[BasePipe]:
        raise NotImplementedError('Specify list of pipes. Set up them in ::start method.')

    def set_up(self, updater: Updater):
        self.updater = updater
        self.dispatcher = updater.dispatcher
        active_user_filter = ActiveUsersFilter(self.active_users)
        for handler in self.commands_handlers:
            handler.filters = active_user_filter

    @property
    def commands_handlers(self) -> List[CommandHandler]:
        return []

    @log
    def start(self):
        """
        Schedule posting for each pipe.
        """
        for pipe in self.pipes:
            pipe.set_up(self.channel_id, self.updater)
            pipe.start_posting_cycle()

    @log
    def add_commands_handlers(self, chat_id):
        """
        Used by manager class when changing channel command namespace.
        """
        self.active_users.add(chat_id)
        for handler in self.commands_handlers:
            self.dispatcher.add_handler(handler)

    @log
    def remove_commands_handlers(self, chat_id):
        """
        Used by manager class when changing channel command namespace.
        """
        self.active_users.remove(chat_id)
        for handler in self.commands_handlers:
            self.dispatcher.remove_handler(handler)

    def help_text(self):
        """
        Used by manager class to print out info about commands specified for channel.
        """
        pass
