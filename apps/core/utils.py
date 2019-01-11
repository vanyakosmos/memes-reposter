import logging
from collections import defaultdict
from typing import Dict, List

from django.conf import settings
from telegram import Message, TelegramError

from memes_reposter import tg_bot


logger = logging.getLogger(__name__)
messages = defaultdict(lambda: [])  # type: Dict[str, List[Message]]


def notify_admins(text: str, type='pending', clean=True):
    if clean:
        for message in messages[type]:
            message.delete()
        messages[type] = []
    for admin in settings.TG_ADMINS:
        try:
            msg = tg_bot.send_message(admin, text)
            messages[type].append(msg)
        except TelegramError as e:
            logger.warning(e)
