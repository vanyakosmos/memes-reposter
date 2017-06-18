import logging

import redis
from telegram import Bot
from telegram import Update
from telegram.ext import Updater, CommandHandler
from telegram.ext.dispatcher import run_async

from autoposter import Scheduler
from src.database import RedisDB
from src.fetcher import GalleryFetcher
from src.filter import PostsFilter
from src.publisher import ImgurPostPublisher
from src.stats import get_stats_image

from settings import DEBUG, PORT, BOT_TOKEN, APP_NAME, REDIS_URL, CHANNEL_ID, CLIENT_ID
from settings import IMGUR_CHECK_INTERVAL, CLEARING_DB_INTERVAL, POSTING_INTERVAL


def error(_: Bot, update: Update, err: Exception):
    logging.warning(f'Update "{update}" caused error "{err}"')


@run_async
def boop(_: Bot, update: Update):
    update.message.reply_text('yeah yeah... back to work...')


def schedule(channel: str, bot: Bot, updater: Updater):
    if DEBUG:
        redis_client = redis.StrictRedis()
    else:
        redis_client = redis.from_url(REDIS_URL)
    db = RedisDB(channel, redis_client)

    fetcher = GalleryFetcher(client_id=CLIENT_ID)
    filtr = PostsFilter(db=db, client_id=CLIENT_ID)
    publisher = ImgurPostPublisher(bot=bot, db=db, channel_id=CHANNEL_ID)

    scheduler = Scheduler(name=channel,
                          job_queue=updater.job_queue,
                          db=db,
                          fetcher=fetcher,
                          filtr=filtr,
                          publisher=publisher,
                          data_collection_interval=IMGUR_CHECK_INTERVAL,
                          data_posting_interval=POSTING_INTERVAL,
                          cleanup_interval=CLEARING_DB_INTERVAL)
    scheduler.run()

    def stats(_: Bot, update):
        dates = db.dates_list()
        file = get_stats_image(dates)
        bot.send_photo(chat_id=update.message.chat_id, photo=file)
        file.close()

    updater.dispatcher.add_handler(CommandHandler(channel + '_stats', stats))


def main():
    bot = Bot(BOT_TOKEN)
    updater = Updater(bot=bot)
    dp = updater.dispatcher

    schedule(channel='telemgur', bot=bot,
             updater=updater)

    dp.add_handler(CommandHandler('boop', boop))
    dp.add_error_handler(error)

    if DEBUG:
        updater.start_polling()
    else:
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=BOT_TOKEN)
        updater.bot.set_webhook(f"https://{APP_NAME}.herokuapp.com/{BOT_TOKEN}")
    updater.idle()


if __name__ == '__main__':
    main()
