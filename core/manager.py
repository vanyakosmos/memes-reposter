import logging

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from core.channel import BaseChannel
from core.decorators import admin_access


class Manager(object):
    def __init__(self, token: str, admins=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.token = token
        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher

        self.channels = {}
        self.chosen_channel = None
        self.admins = admins

    def register(self, channel: BaseChannel):
        channel.set_up(self.updater)
        self.channels[channel.label] = channel

    def activate(self):
        for label, channel in self.channels.items():
            channel.start()
        self.set_up_commands()

    def set_up_commands(self):
        commands = {
            'start': self.command_help,
            'help': self.command_help,
            'list': self.command_list,
            'choose': self.command_choose,
        }
        for name, command in commands.items():
            self.dispatcher.add_handler(CommandHandler(name, command))
        self.dispatcher.add_handler(CallbackQueryHandler(self.command_accept_choice))
        self.dispatcher.add_error_handler(self.command_error)

    def start_polling(self):
        self.activate()

        self.updater.start_polling()
        self.updater.idle()

    def start_webhook(self, listen='127.0.0.1', port=80, url_path='', webhook_url=None):
        self.activate()

        self.updater.start_webhook(listen=listen, port=port, url_path=url_path)
        self.updater.bot.set_webhook(webhook_url)
        self.updater.idle()

    @admin_access()
    def command_help(self, bot: Bot, update: Update):
        text = "/help or /start - print this message.\n" \
               "/choose - choose channels.\n" \
               "/list - print list of available channels.\n"
        if self.chosen_channel:
            channel_help = self.chosen_channel.help_text() or ' - no commands'
            text += f"\n`{self.chosen_channel.label} ({self.chosen_channel.channel_id})` commands:\n" + channel_help
        bot.send_message(chat_id=update.message.chat_id,
                         text=text)

    @admin_access()
    def command_list(self, bot: Bot, update: Update):
        del bot
        text = 'Channels list:\n'
        for label, channel in self.channels.items():
            text += f' - {label} ({channel.name})\n'
        update.message.reply_text(text)

    @admin_access()
    def command_choose(self, bot: Bot, update: Update):
        channels = []
        for label, channel in self.channels.items():
            button = InlineKeyboardButton(text=label, callback_data=label)
            channels.append(button)

        keyboard = [channels]
        reply_markup = InlineKeyboardMarkup(keyboard)

        bot.send_message(chat_id=update.message.chat_id,
                         text='Choose channel.',
                         reply_markup=reply_markup)

    @admin_access()
    def command_accept_choice(self, bot: Bot, update: Update):
        query = update.callback_query
        if self.chosen_channel:
            self.chosen_channel.remove_commands_handlers()
        self.chosen_channel: BaseChannel = self.channels[query.data]
        self.chosen_channel.add_commands_handlers()
        bot.edit_message_text(text=f'Channel "{query.data}" was chosen.',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        update.message = query.message  # because callback update doesn't have message at all,
        self.command_help(bot, update)  # whereas command_help use message.chat_id

    def command_error(self, bot: Bot, update: Update, error):
        del bot
        self.logger.warning('Update "%s" caused error "%s"' % (update, error))
