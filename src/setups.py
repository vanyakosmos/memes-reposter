from typing import List

import redis
import telegram
from telegram import Bot
from telegram import Update
from telegram.ext import CommandHandler

from autoposter import ChannelSetup
from autoposter import Scheduler
from settings import DEBUG, REDIS_URL
from settings import IMGUR_CHECK_INTERVAL, CLEARING_DB_INTERVAL, POSTING_INTERVAL
from src.collectors import ImgurCollector, RedditCollector
from src.database import RedisDB, RedditRedisDB
from src.stats import get_stats_image


class CommonSetup(ChannelSetup):
    def __init__(self, channel_name: str):
        super().__init__(channel_name)
        self.handlers.extend([
            CommandHandler('stats', self.stats),
            CommandHandler('boop', self.boop),
        ])
        self.database: RedisDB

    def stats(self, bot: Bot, update: Update):
        dates = self.database.dates_list()
        file = get_stats_image(dates)
        bot.send_photo(chat_id=update.message.chat_id, photo=file)
        file.close()

    @staticmethod
    def boop(bot: Bot, update: Update):
        del bot
        update.message.reply_text('yeah yeah... back to work...')


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

    def help_text(self):
        return " - /stats - print posting statistic"

    def get_database(self) -> RedisDB:
        if DEBUG:
            redis_client = redis.StrictRedis()
        else:
            redis_client = redis.from_url(REDIS_URL)
        return RedisDB(self.channel_name, redis_client)


class RedditSetup(CommonSetup):
    def __init__(self, channel_name: str):
        super().__init__(channel_name)
        self.handlers.extend([
            CommandHandler('add', self.add_subreddit, pass_args=True),
            CommandHandler('remove', self.remove_subreddit, pass_args=True),
            CommandHandler('show', self.show_subreddits)
        ])
        self.database: RedditRedisDB

    def get_scheduler(self):
        subreddits_scores = self.database.get_subreddits()
        self.collector = RedditCollector(bot=self.bot, db=self.database,
                                         subreddits_scores=subreddits_scores)

        return Scheduler(name=self.channel_name,
                         job_queue=self.updater.job_queue,
                         db=self.database,
                         collector=self.collector,
                         data_collection_interval=IMGUR_CHECK_INTERVAL,
                         data_posting_interval=POSTING_INTERVAL,
                         cleanup_interval=CLEARING_DB_INTERVAL)

    def help_text(self):
        return " - /stats - print posting statistic\n" \
               " - /add <subreddit> <limit> - add new subreddit (or update old one)" \
               " with filtration by chosen score limit\n" \
               " - /remove <subreddit>\n" \
               " - /show - show table of subreddits and limit scores"

    def get_database(self) -> RedisDB:
        if DEBUG:
            redis_client = redis.StrictRedis()
        else:
            redis_client = redis.from_url(REDIS_URL)
        return RedditRedisDB(self.channel_name, redis_client)

    def add_subreddit(self, bot: Bot, update: Update, args: List[str]):
        del bot
        if len(args) != 2:
            update.message.reply_text('Usage: `\\add <subreddit> <score_limit>')
            return

        subreddit, score = args
        score = int(score)
        self.collector.add_subreddit(subreddit, score)
        self.database.add_subreddit(subreddit, score)
        update.message.reply_text(f'Added/updated subreddit "{subreddit}" with score limit {score}')

    def remove_subreddit(self, bot: Bot, update: Update, args: List[str]):
        del bot
        if len(args) != 1:
            update.message.reply_text('Usage: `\\remove <subreddit>`')
            return

        subreddit = args[0]
        self.collector.remove_subreddit(subreddit)
        self.database.remove_subreddit(subreddit)
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
