from django.conf import settings
from telegram import Bot
from telegram.utils.request import Request


bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN,
    request=Request(connect_timeout=120, read_timeout=120),
)
