from typing import List

from telegram import Bot, Update, ParseMode
from telegram.ext import CommandHandler

from core2.decorators import log
from core2.commands import Commander, ArgParser
from .store import ImgurStore


class TagsCommander(Commander):
    def __init__(self, name, store: ImgurStore):
        super().__init__(name)
        self._handler = CommandHandler(self.name, self.callback, pass_args=True)
        self.store = store

    def get_parser(self) -> ArgParser:
        parser, subparsers = self.get_parser_and_subparsers()

        # add
        parser_add = self.get_sub_command(subparsers, 'add',
                                          help='add new tags',
                                          usage='<tag> [<tag>]*')
        parser_add.add_argument('tags', nargs='*')

        # remove
        parser_remove = self.get_sub_command(subparsers, 'remove', aliases=['delete'],
                                             help='remove tags',
                                             usage='<tag> [<tag>]*')
        parser_remove.add_argument('tags', nargs='*')

        # show
        self.get_sub_command(subparsers, 'show', help='show list of banned tags')

        return parser

    def distribute(self, bot: Bot, update: Update, args):
        if args.help:
            self.send_code(update, args.help)

        elif args.command == 'add':
            usage = self.subparsers['add'].format_usage()
            self.add(bot, update, args.tags, usage)

        elif args.command in ['remove', 'delete']:
            usage = self.subparsers['remove'].format_usage()
            self.remove(bot, update, args.tags, usage)

        elif args.command == 'show':
            self.show(bot, update)

        else:
            self.logger.error('Bad args: ' + str(args))
            raise Exception  # will never get this far (hopefully)

    @log
    def show(self, bot: Bot, update: Update):
        del bot
        tags = self.store.get_tags()
        tags = [f'` - {tag}`' for tag in tags]
        tags = '\n'.join(tags) or ' > nothing'
        text = 'Banned tags:\n' + tags
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

    @log
    def add(self, bot: Bot, update: Update, tags: List[str], usage):
        if len(tags) == 0:
            self.send_code(update, usage)
            return
        self.store.add_tags(tags)
        self.show(bot, update)

    @log
    def remove(self, bot: Bot, update: Update, tags: List[str], usage):
        if len(tags) == 0:
            self.send_code(update, usage)
            return
        self.store.remove_tags(tags)
        self.show(bot, update)
