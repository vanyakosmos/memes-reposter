from typing import List

import redis
import telegram
from telegram import Bot
from telegram import Update
from telegram.ext import CommandHandler

from autoposter import Scheduler, ChannelSetup, admin_access
from settings import REDIS_URL, LIST_OF_ADMINS
from settings import IMGUR_CHECK_INTERVAL, CLEARING_DB_INTERVAL, POSTING_INTERVAL
from src.collectors import ImgurCollector, RedditCollector
from src.database import RedisDB, RedditRedisDB
from src.stats import get_stats_image


class CommonSetup(ChannelSetup):
    def __init__(self, channel_name: str):
        super().__init__(channel_name)
        self.handlers.extend([
            CommandHandler('stats', self.command_stats),
            CommandHandler('boop', self.command_boop),
        ])
        self.database: RedisDB

    def command_stats(self, bot: Bot, update: Update):
        dates = self.database.dates_list()
        file = get_stats_image(dates)
        bot.send_photo(chat_id=update.message.chat_id, photo=file)
        file.close()

    @staticmethod
    def command_boop(bot: Bot, update: Update):
        del bot
        update.message.reply_text('yeah, yeah... back to work...')


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
        redis_client = redis.from_url(REDIS_URL)
        return RedisDB(self.channel_name, redis_client)


class RedditSetup(CommonSetup):
    def __init__(self, channel_name: str):
        super().__init__(channel_name)
        self.handlers.extend([
            CommandHandler('add', self.command_add_subreddits, pass_args=True),
            CommandHandler('remove', self.command_remove_subreddits, pass_args=True),
            CommandHandler('show', self.command_show_subreddits)
        ])

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
               " - /add <subreddit> <limit> [<subreddit> <limit> ...] - " \
               " add new subreddit (or update old one)" \
               " with filtration by chosen score limit\n" \
               " - /remove <subreddit> [<subreddit> ...]\n" \
               " - /show - show table of subreddits and limit scores"

    def get_database(self) -> RedisDB:
        redis_client = redis.from_url(REDIS_URL)
        return RedditRedisDB(self.channel_name, redis_client)

    @admin_access(LIST_OF_ADMINS)
    def command_add_subreddits(self, bot: Bot, update: Update, args: List[str]):
        del bot
        usage_string = 'Nothing was added.\n' \
                       'Usage: /add <subreddit:str> <score_limit:int> [<subreddit:str> <score_limit:int> ...]'
        if len(args) == 0 or len(args) % 2 != 0:
            update.message.reply_text(usage_string)
            return

        subreddits = {}
        while args:
            subreddit, score = args[:2]
            args = args[2:]
            if score.isdecimal():
                score = int(score)
            else:
                update.message.reply_text(usage_string)
                return
            subreddits[subreddit] = score
        self.collector.add_subreddits(subreddits)

        answer = "Added/updated subreddits:\n"
        for subreddit, score in subreddits.items():
            answer += f" - {subreddit} ~ {score}\n"
        update.message.reply_text(answer)

    @admin_access(LIST_OF_ADMINS)
    def command_remove_subreddits(self, bot: Bot, update: Update, args: List[str]):
        del bot
        if len(args) == 0 or len(args) < 1:
            update.message.reply_text('Usage: /remove <subreddit> [<subreddit> ...]')
            return

        subreddits = args
        removed = self.collector.remove_subreddits(subreddits)
        answer = 'Removed subreddits:\n'
        for r in removed:
            answer += f' - {r}\n'
        update.message.reply_text(answer)

    def command_show_subreddits(self, bot: Bot, update: Update):
        del bot
        subreddits = self.collector.get_subreddits()
        text = 'List of subreddits:\n' \
               f"`{'subreddit':13s} limit score`\n"

        for sr in subreddits:
            score = subreddits[sr]
            text += f'` - {sr:10s} {score}`\n'
        update.message.reply_text(text, parse_mode=telegram.ParseMode.MARKDOWN)
