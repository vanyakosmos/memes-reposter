import logging

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, CallbackQuery
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from core2.channel import BaseChannel
from core2.decorators import admin_access, log


logger = logging.getLogger(__name__)


class Manager(object):
    def __init__(self, token: str, admins=None):
        self.token = token
        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher

        self.channels = {}
        self.chosen_channels = {}
        self.admins = admins

    @log
    def register(self, channel: BaseChannel):
        channel.set_up(self.updater)
        self.channels[channel.label] = channel

    @log
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
        self.dispatcher.add_handler(CallbackQueryHandler(self.query_callback))
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

    @log
    @admin_access()
    def command_help(self, bot: Bot, update: Update):
        text = "/help or /start - print this message.\n" \
               "/choose - choose channels.\n" \
               "/list - print list of available channels.\n"

        chosen_channel = self.chosen_channels.get(update.message.chat_id, None)
        if chosen_channel:
            help = chosen_channel.help_text() or ' - no commands'
            help = '```\n' + help + '\n```'
            text += f"\n`{chosen_channel.label} ({chosen_channel.channel_id}) commands:`\n" + help
        bot.send_message(chat_id=update.message.chat_id,
                         text=text, parse_mode=ParseMode.MARKDOWN)

    @log
    @admin_access()
    def command_list(self, bot: Bot, update: Update):
        del bot
        text = 'Channels list:\n'
        for label, channel in self.channels.items():
            text += f' - {label} ({channel.channel_id})\n'
        update.message.reply_text(text)

    @log
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

    @log
    def query_callback(self, bot: Bot, update: Update):
        for label, channel in self.channels.items():
            if channel.callback_query(bot, update):
                return

        self.command_accept_choice(bot, update)

    @log
    @admin_access()
    def command_accept_choice(self, bot: Bot, update: Update):
        query: CallbackQuery = update.callback_query
        update.message = query.message  # because callback update doesn't have message at all
        chat_id = update.message.chat_id

        chosen_channel = self.chosen_channels.get(chat_id, None)
        if chosen_channel:
            chosen_channel.remove_commands_handlers(chat_id)

        chosen_channel: BaseChannel = self.channels[query.data]
        self.chosen_channels[chat_id] = chosen_channel
        chosen_channel.add_commands_handlers(chat_id)

        bot.edit_message_text(text=f'Chose {query.data} ({chosen_channel.channel_id}).',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        help = chosen_channel.help_text()
        update.message.reply_text('```\n' + help + '\n```', parse_mode=ParseMode.MARKDOWN)

    @log
    def command_error(self, bot: Bot, update: Update, error):
        del bot
        logger.warning('Update "%s" caused error "%s"' % (update, error))
