from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler

from core.channel import BaseChannel
from core.commands import ActivityCommander, SettingsCommander
from core.decorators import log
from settings import CLEAR_AGE, REDDIT_CHANNEL_ID, MONGODB_URI
from .commands import SubredditsCommander
from .pipes import RedditPipe
from .settings import RedditSettings
from .store import RedditStore


class RedditChannel(BaseChannel):
    def __init__(self):
        super().__init__()
        self.store = RedditStore(name='reddit',
                                 url=MONGODB_URI,
                                 clear_age=CLEAR_AGE)
        self.settings = RedditSettings(self.store)

        self.commanders = [
            SubredditsCommander('subs', self.store),
            SettingsCommander('sets', self.settings),
            ActivityCommander('act', self.store),
        ]

    def get_channel_id(self):
        return REDDIT_CHANNEL_ID

    def get_pipes(self):
        return [RedditPipe()]

    @property
    def commands_handlers(self):
        return [c.handler for c in self.commanders]

    @log
    def start(self):
        for pipe in self.pipes:
            pipe.set_up(self.channel_id, self.updater, store=self.store, settings=self.settings)
            pipe.start_posting_cycle()

    def help_text(self):
        return '\n'.join([c.get_usage() for c in self.commanders])

    def callback_handler(self, bot: Bot, update: Update):
        query = update.callback_query
        data = query.data.split(':')

        if data[0] != 'reddit':
            self.logger.debug('not reddit button')
            return

        post_id, data = data[1], data[2]

        if data != 'clap':
            self.logger.debug('not a clap')
            return

        post = self.store.get_post(post_id)

        if post is None:
            self.logger.debug('no such post anymore')
            return

        self.store.clap(post_id)

        claps = post['claps'] + 1
        clap_button = f'👏 {claps}'

        row = []
        if post['type'] not in ('text', 'link'):
            row.append(InlineKeyboardButton('original', url=post['url']))
        row.append(InlineKeyboardButton('comments', url=post['comments']))
        row.append(InlineKeyboardButton(clap_button, callback_data=f'reddit:{post_id}:clap'))
        markup = InlineKeyboardMarkup([row])
        query.edit_message_reply_markup(reply_markup=markup)
