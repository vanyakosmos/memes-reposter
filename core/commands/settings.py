from telegram import Bot, Update, ParseMode
from telegram.ext import CommandHandler

from core.decorators import log
from core.settings import SettingsError, Settings
from core.commands import Commander, ArgParser


class SettingsCommander(Commander):
    def __init__(self, name, settings: Settings, restart_callback):
        super().__init__(name)
        self._handler = CommandHandler(self.name, self.callback, pass_args=True)
        self.settings = settings
        self.restart_callback = restart_callback

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
