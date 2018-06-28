from django.conf import settings
from telegram import Bot


bot = Bot(settings.TELEGRAM_BOT_TOKEN)
