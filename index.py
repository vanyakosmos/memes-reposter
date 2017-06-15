import logging
import os

import redis
from telegram import Bot
from telegram import Update
from telegram.ext import Updater, CommandHandler

from src.database import RedisDB
from src.scheduler import scheduling
from src.stats import get_stats_image
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

    def stats(bot: Bot, update):
        dates = db.dates_list()
        file = get_stats_image(dates)
        bot.send_photo(chat_id=update.message.chat_id, photo=file)
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
