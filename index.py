import json
import logging
import os
from io import BytesIO

import redis
from telegram import Update
from telegram.ext import Updater, CommandHandler

from src.database import RedisDB
from src.scheduler import scheduling
from settings import DEBUG, PORT, BOT_TOKEN, APP_NAME


logger = logging.getLogger(__name__)


def error(_, update, err):
    logger.warning(f'Update "{update}" caused error "{err}"')


def boop(_, update: Update):
    update.message.reply_text('yeah yeah... back to work...')


def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    if DEBUG:
        redis_client = redis.StrictRedis()
    else:
        redis_client = redis.from_url(os.environ.get("REDIS_URL"))
    db = RedisDB(redis_client)

    scheduling(updater.job_queue, db)

    def stats(bot, update):
        dates = db.dates_list()
        file = BytesIO()
        file.name = "cache.json"
        file.write(
            json.dumps(
                list(map(int, dates)),
                indent=4,
                sort_keys=True,
                ensure_ascii=False
            ).encode("utf-8"))

        file.seek(0)
        bot.sendDocument(chat_id=update.message.chat_id, document=file)
        file.close()

    dp.add_handler(CommandHandler('boop', boop))
    dp.add_handler(CommandHandler('stats', stats))
    dp.add_error_handler(error)

    if DEBUG:
        updater.start_polling()
    else:
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=BOT_TOKEN)
        updater.bot.set_webhook(f"https://{APP_NAME}.herokuapp.com/" + BOT_TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
