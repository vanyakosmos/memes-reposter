from telegram import Bot, Update, ParseMode
from telegram.ext import CommandHandler

from core.decorators import log
from core.settings import SettingsError
from core.commands import Commander, ArgParser
from .settings import ImgurSettings
from .store import ImgurStore


class TagsCommander(Commander):
    def __init__(self, store: ImgurStore):
        super().__init__()
        self._handler = CommandHandler(self.name, self.callback, pass_args=True)
        self.store = store

    def get_name(self) -> str:
        return 'tags'

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
            self.add(bot, update, args)
        elif args.command in ['remove', 'delete']:
            self.remove(bot, update, args)
        elif args.command == 'show':
            self.show(bot, update)
        else:
            raise Exception  # will never get this far (hopefully)

    @log
    def show(self, bot: Bot, update: Update):
        del bot
        tags = self.store.get_tags()
        tags = [f'` - {tag}`' for tag in tags]
        tags = '\n'.join(tags)
        text = 'Banned tags:\n' + tags
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

    @log
    def add(self, bot: Bot, update: Update, args):
        if len(args.tags) == 0:
            usage = self.subparsers[args.command].format_usage()
            self.send_code(update, usage)
            return
        self.store.add_tags(args.tags)
        self.show(bot, update)

    @log
    def remove(self, bot: Bot, update: Update, args):
        if len(args.tags) == 0:
            usage = self.subparsers[args.command].format_usage()
            self.send_code(update, usage)
            return
        self.store.remove_tags(args.tags)
        self.show(bot, update)


class SettingsCommander(Commander):
    def __init__(self, settings: ImgurSettings, restart_callback):
        super().__init__()
        self._handler = CommandHandler(self.name, self.callback, pass_args=True)
        self.settings = settings
        self.restart_callback = restart_callback

    def get_name(self) -> str:
        return 'settings'

    def get_parser(self) -> ArgParser:
        parser, subparsers = self.get_parser_and_subparsers()

        # edit
        parser_edit = self.get_sub_command(subparsers, 'edit',
                                           help='edit setting',
                                           usage='<setting> <value>')
        parser_edit.add_argument('keys', nargs=2)

        # show
        self.get_sub_command(subparsers, 'show', help='show list of settings')

        return parser

    def distribute(self, bot: Bot, update: Update, args):
        if args.help:
            self.send_code(update, args.help)
        elif args.command == 'edit':
            self.edit(bot, update, args)
        elif args.command == 'show':
            self.show(bot, update)
        else:
            raise Exception  # will never get this far (hopefully)

    @log
    def show(self, bot: Bot, update: Update):
        del bot
        ss = []
        for key, value in self.settings.items():
            ss.append(f'` - {key} = {value}`')
        ss = '\n'.join(ss)
        msg = 'Settings list:\n' + ss
        update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    @log
    def edit(self, bot: Bot, update: Update, args):
        if len(args.keys) != 2:
            usage = self.subparsers[args.command].format_usage()
            self.send_code(update, usage)
            return

        key, value = args.keys
        try:
            self.settings.set(key, value)
            self.restart_callback()
        except SettingsError as e:
            update.message.reply_text(str(e))
        self.show(bot, update)
