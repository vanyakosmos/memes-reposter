from typing import List

from telegram import Bot, Update, ParseMode
from telegram.ext import CommandHandler

from core.channel import BaseChannel
from core.decorators import log
from settings import REDIS_URL, REDDIT_CHANNEL_ID
from .pipes import RedditPipe
from .store import RedditStore


class RedditChannel(BaseChannel):
    def __init__(self):
        super().__init__()
        self.commands_handlers = [
            CommandHandler('add', self.command_add, pass_args=True),
            CommandHandler('remove', self.command_remove, pass_args=True),
            CommandHandler('show', self.command_list),
        ]
        self.store = RedditStore('reddit',
                                 url=REDIS_URL,
                                 clear_age=1 * 60 * 60)  # fixme: clear age and interval must be in one place (?)
        self.pipes = [RedditPipe()]

    def get_channel_id(self):
        return REDDIT_CHANNEL_ID

    @log
    def start(self):
        for pipe in self.pipes:
            pipe.set_up(self.channel_id, self.updater, self.store)
            pipe.start_posting_cycle()

    def help_text(self):
        lines = [
            '/add - add/update subreddits. '
            'Usage: "/add <subreddit> <score_limit> [<subreddit> <score_limit>]*"',
            '/remove - remove subreddits. Usage: "/remove <subreddit> [<subreddit>]*"',
            '/show - show list of subreddits and their score limits. Usage: "/show"'
        ]

        return '\n'.join([' - ' + line for line in lines])

    @log
    def command_add(self, bot: Bot, update: Update, args: List[str]):
        usage_string = ('Nothing was added.\n'
                        'Usage: `/add <subreddit> <score_limit> [<subreddit> <score_limit>]*`')
        if len(args) == 0 or len(args) % 2 != 0:
            update.message.reply_text(usage_string, parse_mode=ParseMode.MARKDOWN)
            return

        subreddits = {}
        while args:
            name, score = args[:2]
            args = args[2:]
            if score.isdecimal():
                score = int(score)
            else:
                update.message.reply_text(usage_string)
                return
            subreddits[name] = score

        self.store.add(subreddits)
        self.command_list(bot, update)

    @log
    def command_remove(self, bot: Bot, update: Update, args: List[str]):
        if len(args) == 0 or len(args) < 1:
            update.message.reply_text('Usage: /remove <subreddit> [<subreddit> ...]')
            return

        self.store.remove(args)
        self.command_list(bot, update)

    @log
    def command_list(self, bot: Bot, update: Update):
        del bot
        subreddits = self.store.get()
        title = 'subreddit'.ljust(13)
        text = f"`{title} limit score`\n"

        for name, score in subreddits.items():
            text += f'` - {name:10s} {score}`\n'
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
