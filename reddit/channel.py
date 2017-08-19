from typing import List

from telegram import Bot, Update, ParseMode
from telegram.ext import Updater, CommandHandler

from telegram_autoposter.channel import Channel
from settings import reddit_settings, REDIS_URL
from .pipes import RedditPipe
from .store import RedisStore


class RedditChannel(Channel):
    name = reddit_settings['channel_id']
    pipes = [RedditPipe]

    def __init__(self, updater: Updater):
        super().__init__(updater)
        self.commands_handlers = [
            CommandHandler('add', self.command_add, pass_args=True),
            CommandHandler('remove', self.command_remove, pass_args=True),
            CommandHandler('show', self.command_list),
            CommandHandler('setting', self.command_setting, pass_args=True),
        ]
        self.store = RedisStore('reddit',
                                url=REDIS_URL,
                                clear_age=reddit_settings['db_clear_age'])
        self.store.set_up_settings(post_interval=reddit_settings['post_interval'])
        self.pipe = RedditPipe(self.name, self.updater, self.store)

    def start_posting(self):
        self.pipe.schedule_posts()

    def help_text(self):
        # markdown:
        lines = [
            '/add - add/update subreddits. '
            'Usage: /add `<subreddit> <score_limit> [<subreddit> <score_limit>]*`',
            '/remove - remove subreddits. Usage: `/remove <subreddit> [<subreddit>]*`',
            '/show - show list of subreddits and their score limits. Usage: `/show`'
        ]

        return '\n'.join([' - ' + line for line in lines])

    def command_add(self, bot: Bot, update: Update, args: List[str]):
        del bot
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

        answer = "Added/updated subreddits:\n"
        for name, score in subreddits.items():
            answer += f" - {name} ~ {score}\n"
        update.message.reply_text(answer)

    def command_remove(self, bot: Bot, update: Update, args: List[str]):
        del bot
        if len(args) == 0 or len(args) < 1:
            update.message.reply_text('Usage: /remove <subreddit> [<subreddit> ...]')
            return

        subreddits = args
        removed = self.store.remove(subreddits)
        answer = 'Removed subreddits:\n'
        for r in removed:
            answer += f' - {r}\n'
        update.message.reply_text(answer)

    def command_list(self, bot: Bot, update: Update):
        del bot
        subreddits = self.store.get()
        text = 'List of subreddits:\n' \
               f"`{'subreddit':13s} limit score`\n"

        for name, score in subreddits.items():
            text += f'` - {name:10s} {score}`\n'
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

    def command_setting(self, bot: Bot, update: Update, args: List[str]):
        del bot
        usage_string = ('Nothing was added.\n'
                        'Usage: `/setting <key> <value>`')
        if len(args) != 2:
            update.message.reply_text(usage_string, parse_mode=ParseMode.MARKDOWN)
            return
        key, value = args
        changed = self.store.change_setting(key, value)
        if changed:
            self.pipe.schedule_posts()
            update.message.reply_text('updated')
        else:
            update.message.reply_text('bad setting key')
