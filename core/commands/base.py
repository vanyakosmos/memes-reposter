import logging
import argparse
from typing import List

from telegram import Bot, Update, ParseMode
from telegram.ext import CommandHandler


class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        msg = 'Error:\n'
        msg += self.format_usage()
        msg += message
        raise argparse.ArgumentError(msg)


class HelpAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help=None, **kwargs):
        super(HelpAction, self).__init__(
            option_strings=option_strings,
            dest=dest, default=default,
            nargs=0, help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        msg = parser.format_help()
        setattr(namespace, self.dest, msg)


class Commander(object):
    def __init__(self, name):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = name
        self._handler = CommandHandler(self.name, self.callback, pass_args=True)
        self.subparsers = {}
        self.parser = self.get_parser()

    @property
    def handler(self):
        return self._handler

    def get_parser(self) -> ArgParser:
        parser, _ = self.get_parser_and_subparsers()
        return parser

    def get_parser_and_subparsers(self):
        parser = ArgParser(prog='/' + self.name, add_help=False, conflict_handler='resolve')
        parser.add_argument(dest='help', action=HelpAction)
        parser.add_argument('-h', '--help', action=HelpAction, default=None)
        subparsers = parser.add_subparsers(title='commands', dest='command')
        return parser, subparsers

    def get_sub_command(self, subparsers, name, help='', usage=None, aliases=None):
        if usage:
            usage = f'/{self.name} {name} {usage}'
        if aliases is None:
            aliases = []
        parser = subparsers.add_parser(name, aliases=aliases,
                                       add_help=False, conflict_handler='resolve',
                                       help=help, usage=usage)
        parser.add_argument('-h', '--help', action=HelpAction, default=None)
        self.subparsers[name] = parser
        return parser

    def callback(self, bot: Bot, update: Update, args: List[str]):
        try:
            args = self.parser.parse_args(args)
        except argparse.ArgumentError as e:
            self.send_code(update, str(e))
            return
        self.distribute(bot, update, args)

    def send_code(self, update: Update, text: str):
        update.message.reply_text('```\n' + text + '\n```', parse_mode=ParseMode.MARKDOWN)

    def distribute(self, bot: Bot, update: Update, args):
        if args.help:
            self.send_code(update, args.help)

    def get_usage(self):
        return self.parser.format_usage().replace('usage: ', '', 1).strip()
