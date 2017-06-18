import logging

import redis
from telegram import Bot
from telegram import Update
from telegram.ext import Updater, CommandHandler
from telegram.ext.dispatcher import run_async

from autoposter import Scheduler
from src.database import RedisDB
from src.fetcher import GalleryFetcher, SubredditFetcher
from src.filter import PostsFilter
from src.publisher import ImgurPostPublisher, SubredditPublisher
from src.stats import get_stats_image

from settings import TELEMGUR_CHANNEL_ID, SUBREDDIT_CHANNEL_ID
from settings import DEBUG, PORT, BOT_TOKEN, APP_NAME, REDIS_URL, CLIENT_ID
from settings import IMGUR_CHECK_INTERVAL, CLEARING_DB_INTERVAL, POSTING_INTERVAL


def error(_: Bot, update: Update, err: Exception):
    logging.warning(f'Update "{update}" caused error "{err}"')


@run_async
def boop(_: Bot, update: Update):
    update.message.reply_text('yeah yeah... back to work...')


def schedule_telemgur(bot: Bot, updater: Updater):
    channel_name = 'telemgur'
    if DEBUG:
        redis_client = redis.StrictRedis()
    else:
        redis_client = redis.from_url(REDIS_URL)
    db = RedisDB(channel_name, redis_client)

    fetcher = GalleryFetcher()
    filtr = PostsFilter(db=db)
    publisher = ImgurPostPublisher(bot=bot, db=db, channel_id=TELEMGUR_CHANNEL_ID)

    scheduler = Scheduler(name=channel_name,
                          job_queue=updater.job_queue,
                          db=db,
                          fetchers=[fetcher],
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

    updater.dispatcher.add_handler(CommandHandler(channel_name + '_stats', stats))


def schedule_pop_subreddits(bot: Bot, updater: Updater):
    channel_name = 'pop_reddit'
    if DEBUG:
        redis_client = redis.StrictRedis()
    else:
        redis_client = redis.from_url(REDIS_URL)
    db = RedisDB(channel_name, redis_client)

    subreddits = [
        'funny',
        'aww',
        'pics',
        'gifs',
    ]

    fetchers = [SubredditFetcher(subreddit=subreddit) for subreddit in subreddits]
    filtr = PostsFilter(db=db)
    publisher = SubredditPublisher(bot=bot, db=db, channel_id=SUBREDDIT_CHANNEL_ID)

    scheduler = Scheduler(name=channel_name,
                          job_queue=updater.job_queue,
                          db=db,
                          fetchers=fetchers,
                          filtr=filtr,
                          publisher=publisher,
                          data_collection_interval=30*60,  # 30m
                          data_posting_interval=10,
                          cleanup_interval=CLEARING_DB_INTERVAL)
    scheduler.run()

    def stats(_: Bot, update):
        dates = db.dates_list()
        file = get_stats_image(dates)
        bot.send_photo(chat_id=update.message.chat_id, photo=file)
        file.close()

    updater.dispatcher.add_handler(CommandHandler(channel_name + '_stats', stats))


def main():
    bot = Bot(BOT_TOKEN)
    updater = Updater(bot=bot)
    dp = updater.dispatcher

    schedule_telemgur(bot=bot, updater=updater)
    schedule_pop_subreddits(bot=bot, updater=updater)

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
