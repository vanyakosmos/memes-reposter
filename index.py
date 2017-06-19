import logging
from typing import List

import redis
import telegram
from telegram import Bot
from telegram import Update
from telegram.ext import Updater, CommandHandler
from telegram.ext.dispatcher import run_async

from autoposter import Scheduler
from settings import DEBUG, PORT, BOT_TOKEN, APP_NAME, REDIS_URL
from settings import IMGUR_CHECK_INTERVAL, CLEARING_DB_INTERVAL, POSTING_INTERVAL
from src.collectors import ImgurCollector, RedditCollector
from src.database import RedisDB
from src.stats import get_stats_image


def error(_: Bot, update: Update, err: Exception):
    logging.warning(f'Update "{update}" caused error "{err}"')


@run_async
def boop(_: Bot, update: Update):
    update.message.reply_text('yeah yeah... back to work...')


class CommonSetup(object):
    def __init__(self, channel_name: str, bot: Bot, updater: Updater):
        self.channel_name = channel_name
        self.bot = bot
        self.updater = updater
        self.collector = None
        self.dp = updater.dispatcher
        self.database = self.get_database()
        self.scheduler = self.get_scheduler()
        self.setup_commands()

    def get_scheduler(self) -> Scheduler:
        pass

    def start(self):
        self.scheduler.run()

    def setup_commands(self):
        self.dp.add_handler(CommandHandler(self.channel_name + '_stats', self.stats))

    def get_database(self) -> RedisDB:
        if DEBUG:
            redis_client = redis.StrictRedis()
        else:
            redis_client = redis.from_url(REDIS_URL)
        return RedisDB(self.channel_name, redis_client)

    def stats(self, bot: Bot, update: Update):
        dates = self.database.dates_list()
        file = get_stats_image(dates)
        bot.send_photo(chat_id=update.message.chat_id, photo=file)
        file.close()


class ImgurSetup(CommonSetup):
    def get_scheduler(self):
        self.collector = ImgurCollector(bot=self.bot, db=self.database)
        return Scheduler(name=self.channel_name,
                         job_queue=self.updater.job_queue,
                         db=self.database,
                         collector=self.collector,
                         data_collection_interval=IMGUR_CHECK_INTERVAL,
                         data_posting_interval=POSTING_INTERVAL,
                         cleanup_interval=CLEARING_DB_INTERVAL)


class RedditSetup(CommonSetup):
    def get_scheduler(self):
        self.collector = RedditCollector(bot=self.bot, db=self.database)

        return Scheduler(name=self.channel_name,
                         job_queue=self.updater.job_queue,
                         db=self.database,
                         collector=self.collector,
                         data_collection_interval=IMGUR_CHECK_INTERVAL,
                         data_posting_interval=POSTING_INTERVAL,
                         cleanup_interval=CLEARING_DB_INTERVAL)

    def setup_commands(self):
        super().setup_commands()
        # self.dp.add_handler(CommandHandler(self.channel_name + '_add', self.add_subreddit, pass_args=True))
        # self.dp.add_handler(CommandHandler(self.channel_name + '_remove', self.remove_subreddit, pass_args=True))
        self.dp.add_handler(CommandHandler(self.channel_name + '_show', self.show_subreddits))

    def add_subreddit(self, bot: Bot, update: Update, args: List[str]):
        del bot
        if len(args) != 2:
            update.message.reply_text('Usage: \\<channel_name>_add <subreddit> <score_limit>')
            return

        subreddit, score = args
        self.collector.add_subreddit(subreddit, int(score))
        update.message.reply_text(f'Added subreddit "{subreddit}" with score limit {score}')

    def remove_subreddit(self, bot: Bot, update: Update, args: List[str]):
        del bot
        if len(args) != 1:
            update.message.reply_text('Usage: \\<channel_name>_remove <subreddit>')
            return

        subreddit = args[0]
        self.collector.remove_subreddit(subreddit)
        update.message.reply_text(f'Removed subreddit "{subreddit}".')

    def show_subreddits(self, bot: Bot, update: Update):
        del bot

        subreddits = self.collector.get_subreddits()
        text = 'List of subreddits:\n' \
               f"`{'subreddit':13s} limit score`\n"

        for sr in subreddits:
            score = subreddits[sr]
            text += f'` - {sr:10s} {score}`\n'
        update.message.reply_text(text, parse_mode=telegram.ParseMode.MARKDOWN)


def main():
    bot = Bot(BOT_TOKEN)
    updater = Updater(bot=bot)
    dp = updater.dispatcher

    imgur_setup = ImgurSetup('telemgur', bot, updater)
    imgur_setup.start()

    reddit_setup = RedditSetup('pop_reddit', bot, updater)
    reddit_setup.start()

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
