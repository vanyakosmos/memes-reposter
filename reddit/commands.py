from typing import List

from telegram import Bot, Update, ParseMode
from telegram.ext import CommandHandler

from core.decorators import log
from core.commands import Commander, ArgParser
from .store import RedditStore


class SubredditsCommander(Commander):
    def __init__(self, name, store: RedditStore):
        super().__init__(name)
        self._handler = CommandHandler(self.name, self.callback, pass_args=True)
        self.store = store

    def get_parser(self) -> ArgParser:
        parser, subparsers = self.get_parser_and_subparsers()

        # add
        parser_add = self.get_sub_command(subparsers, 'add',
                                          help='update (add/edit) subreddit',
                                          usage='<name> <score limit>')
        parser_add.add_argument('keys', nargs=2)

        # remove
        parser_remove = self.get_sub_command(subparsers, 'remove', aliases=['delete'],
                                             help='remove subreddits',
                                             usage='<name> [<name>]*')
        parser_remove.add_argument('keys', nargs='+')

        # show
        self.get_sub_command(subparsers, 'show', help='show list of subreddits and its score limits')

        return parser

    def distribute(self, bot: Bot, update: Update, args):
        if args.help:
            self.send_code(update, args.help)

        elif args.command == 'add':
            usage = self.subparsers['add'].format_usage()
            self.add(bot, update, args.keys, usage)

        elif args.command in ['remove', 'delete']:
            usage = self.subparsers['remove'].format_usage()
            self.remove(bot, update, args.keys, usage)

        elif args.command == 'show':
            self.show(bot, update)

        else:
            self.logger.error('Bad args: ' + str(args))
            raise Exception  # will never get this far (hopefully)

    @log
    def show(self, bot: Bot, update: Update):
        del bot
        subreddits = self.store.get()
        title = 'subreddit'.ljust(13)
        text = f"`{title} limit score`\n"

        for name, score in subreddits.items():
            text += f'` - {name:10s} {score}`\n'
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

    @log
    def add(self, bot: Bot, update: Update, args: List[str], usage: str):
        if len(args) != 2:
            self.send_code(update, usage)
            return

        subreddits = {}
        name, score = args
        if score.isdecimal():
            score = int(score)
        else:
            self.send_code(update, usage)
            return
        subreddits[name] = score

        self.store.add(subreddits)
        self.show(bot, update)

    @log
    def remove(self, bot: Bot, update: Update, args: List[str], usage: str):
        if len(args) < 1:
            self.send_code(update, usage)
            return

        self.store.remove(args)
        self.show(bot, update)
