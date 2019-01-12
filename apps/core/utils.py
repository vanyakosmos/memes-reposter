import logging
from collections import defaultdict
from typing import Dict, List, Iterable

from django.conf import settings
from telegram import Message, TelegramError

from memes_reposter import tg_bot


logger = logging.getLogger(__name__)
messages = defaultdict(lambda: [])  # type: Dict[str, List[Message]]


# todo: move to tg app
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


def format_object_repr(obj, fields: Iterable[str]):
    fs = ', '.join([f'{field}="{getattr(obj, field, None)}"' for field in fields])
    return f'<{obj.__class__.__name__}: {fs}>'
