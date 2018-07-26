import logging

from django.conf import settings
from telegram import TelegramError

from memes_reposter.telegram_bot import bot


logger = logging.getLogger(__name__)


def notify_admins(message: str):
    for admin in settings.ADMINS:
        try:
            bot.send_message(admin, message)
        except TelegramError as e:
            logger.warning(e)
