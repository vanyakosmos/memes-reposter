from typing import List

from telegram import Bot, Update, ParseMode
from telegram.ext import CommandHandler

from core.settings import SettingsError
from core.channel import BaseChannel
from core.decorators import log
from settings import REDIS_URL, IMGUR_CHANNEL_ID
from .pipes import ImgurPipe
from .store import ImgurStore
from .settings import ImgurSettings


class ImgurChannel(BaseChannel):
    def __init__(self):
        super().__init__()
        self.commands_handlers = [
            CommandHandler('get_tags', self.command_get_tags),
            CommandHandler('add_tags', self.command_add_tags, pass_args=True),
            CommandHandler('remove_tags', self.command_remove_tags, pass_args=True),
            CommandHandler('settings', self.command_get_settings),
            CommandHandler('setting', self.command_change_setting, pass_args=True),
        ]
        self.store = ImgurStore('imgur',
                                url=REDIS_URL,
                                clear_age=2 * 24 * 60 * 60)
        self.settings = ImgurSettings(self.store)
        self.pipes = [ImgurPipe()]

    def get_channel_id(self):
        return IMGUR_CHANNEL_ID

    @log
    def start(self):
        for pipe in self.pipes:
            pipe.set_up(self.channel_id, self.updater, self.store, self.settings)
            pipe.start_posting_cycle()

    def help_text(self):
        lines = [
            '/get_tags - get list of banned tags',
            '/add_tags',
            '/remove_tags',
            '/settings - get list of settings',
            '/setting <key> <value> - set up various settings such as "post_len" and "long_post_len"',
        ]
        return '\n'.join([' - ' + line for line in lines])

    @log
    def command_get_tags(self, bot: Bot, update: Update):
        del bot
        tags = self.store.get_tags()
        tags = [f'` - {tag}`' for tag in tags]
        tags = '\n'.join(tags)
        text = 'Banned tags:\n' + tags
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

    @log
    def command_add_tags(self, bot: Bot, update: Update, args: List[str]):
        help_msg = 'Usage: `/add_tags <tag> [<tag>]*`'
        if len(args) == 0:
            update.message.reply_text(help_msg, parse_mode=ParseMode.MARKDOWN)
            return
        self.store.add_tags(args)
        self.command_get_tags(bot, update)

    @log
    def command_remove_tags(self, bot: Bot, update: Update, args: List[str]):
        help_msg = 'Usage: `/remove_tags <tag> [<tag>]*`'
        if len(args) == 0:
            update.message.reply_text(help_msg, parse_mode=ParseMode.MARKDOWN)
            return
        self.store.remove_tags(args)
        self.command_get_tags(bot, update)

    @log
    def command_get_settings(self, bot: Bot, update: Update):
        del bot
        ss = []

        for key, value in self.settings.items():
            ss.append(f'` - {key} = {value}`')
        ss = '\n'.join(ss)
        msg = 'Settings list:\n' + ss
        update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    @log
    def command_change_setting(self, bot: Bot, update: Update, args: List[str]):
        help_msg = 'Usage: `/setting <key> <value>`'
        if len(args) != 2:
            update.message.reply_text(help_msg, parse_mode=ParseMode.MARKDOWN)
            return

        key, value = args
        try:
            self.settings.set(key, value)
            self.start()
        except SettingsError as e:
            update.message.reply_text(str(e))
        self.command_get_settings(bot, update)
