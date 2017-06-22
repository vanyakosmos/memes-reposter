import logging
from functools import wraps
from typing import Dict

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from .channel_setup import ChannelSetup


def admin_access(admins_ids):
    """
    Decorator for setting up access restriction. 
    Applicable only to class methods with command signature::

        spam(self, bot: telegram.Bot, update: telegram.Update)

    Args:
        admins_ids: List of administrators ids.

    Returns:
        Wrapper for function wrapper.
    """
    def access(func):
        @wraps(func)
        def wrapped(self, bot: Bot, update: Update, *args, **kwargs):
            user = update.effective_user
            if user.id not in admins_ids:
                self.logger.info(f"Unauthorized access denied for {user}.")
                return
            return func(self, bot, update, *args, **kwargs)
        return wrapped
    return access


class Manager(object):
    def __init__(self, token):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.bot = Bot(token)
        self.updater = Updater(bot=self.bot)
        self.dispatcher = self.updater.dispatcher
        self.setups: Dict[str, ChannelSetup] = {}
        self.chosen_channel: ChannelSetup = None
        self._setup_commands()

    def register(self, *setups: ChannelSetup):
        self.logger.debug('Registering setups...')
        for setup in setups:
            setup.setup_dependencies(self.bot, self.updater, self.dispatcher)
            self.setups[setup.name] = setup

    def unregister(self, channel_name):
        self.logger.debug('Unregistering setups...')
        del self.setups[channel_name]

    def start_polling(self):
        self.logger.debug('Start polling...')
        for setup in self.setups.values():
            setup.start()
        self.updater.start_polling()
        self.updater.idle()

    def start_webhook(self, webhook_url, listen, port, url_path):
        self.logger.debug('Start webhook...')
        for setup in self.setups.values():
            setup.start()
        self.updater.start_webhook(listen=listen, port=port, url_path=url_path)
        self.updater.bot.set_webhook(webhook_url)
        self.updater.idle()

    def _setup_commands(self):
        self.dispatcher.add_handler(CommandHandler('start', self.command_help))
        self.dispatcher.add_handler(CommandHandler('help', self.command_help))
        self.dispatcher.add_handler(CommandHandler('chlist', self.command_show_channels))
        self.dispatcher.add_handler(CommandHandler('choose', self.command_choose))
        self.dispatcher.add_handler(CallbackQueryHandler(self.command_accept_choice))
        self.dispatcher.add_error_handler(self.command_error)

    def command_help(self, bot: Bot, update: Update):
        self.logger.debug('Call /help command.')
        text = "/help or /start - print this message.\n" \
               "/choose - choose channels.\n" \
               "/chlist - print out channels list.\n"
        if self.chosen_channel:
            t = self.chosen_channel.help_text()
            channels_help_text = t if t else ''
            text += f"{self.chosen_channel.name} commands:\n" + channels_help_text

        bot.send_message(chat_id=update.message.chat_id,
                         text=text)

    def command_show_channels(self, bot: Bot, update: Update):
        self.logger.debug('Call /chlist command.')
        del bot
        text = 'Channels list:\n'
        for setup_name in self.setups:
            text += f' - {setup_name}\n'
        update.message.reply_text(text)

    def command_choose(self, bot: Bot, update: Update):
        self.logger.debug('Call /choose command.')
        channels = []
        for setup_name in self.setups:
            button = InlineKeyboardButton(text=setup_name, callback_data=setup_name)
            channels.append(button)

        keyboard = [channels]
        reply_markup = InlineKeyboardMarkup(keyboard)

        bot.send_message(chat_id=update.message.chat_id,
                         text='Choose channel.',
                         reply_markup=reply_markup)

    def command_accept_choice(self, bot: Bot, update: Update):
        self.logger.debug('Query callback after choosing channel.')
        query = update.callback_query
        if self.chosen_channel:
            self.chosen_channel.remove_command_handlers()
        self.chosen_channel = self.setups[query.data]
        self.chosen_channel.add_commands_handlers()
        bot.edit_message_text(text=f'Channel "{query.data}" was chosen.',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        update.message = query.message  # because callback update doesn't have message at all,
        self.command_help(bot, update)  # whereas command_help use message.chat_id

    def command_error(self, bot: Bot, update: Update, error):
        del bot
        self.logger.warning('Update "%s" caused error "%s"' % (update, error))
