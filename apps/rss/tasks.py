import logging
import traceback
from time import sleep
from typing import List

from celery import group
from celery.schedules import crontab
from django.conf import settings

from apps.core.models import SiteConfig, Stat
from memes_reposter.celery import app as celery_app
from memes_reposter.telegram_bot import bot
from .fetcher import fetch_posts
from .models import Channel, Post, RssFeed
from .publisher import publish_post


logger = logging.getLogger(__name__)


def publish_posts(feed: RssFeed, posts: List[Post], ) -> int:
    logger.info(f"Publishing {len(posts)} post(s) from {repr(feed.link)}...")
    counter = 0
    for i, post in enumerate(posts):
        try:
            post.feed = feed
            published = publish_post(bot, feed.channel, post)
            if published:
                logger.info('> Published %d/%d %s', i + 1, len(posts), repr(post.title))
                counter += 1
                sleep(0.5)
            else:
                logger.debug('> 🔥 Skip %d/%d %s', i + 1, len(posts), repr(post.title))
        except Exception as e:
            logger.error('Error %s for post: %s', e, repr(post))
            logger.error(traceback.format_exc())
    logger.info(f"Done {counter}.")
    return counter


def refresh_channels_meta() -> list:
    logger.info('Refreshing channels info...')
    channels = Channel.objects.all()
    stats = []
    for channel in channels:
        chat = bot.get_chat(chat_id=channel.chat_id)

        refreshed = any(map(lambda a: a[0] != a[1], zip(
            [channel.identifier, channel.username, channel.title],
            [str(chat.id), chat.username, chat.title])))
        if refreshed:
            stats.append(channel.title)

        channel.save(bot=bot)
    logger.info('Done.')
    return stats


@celery_app.task
def publish_feed(feed_id: int):
    feed = RssFeed.objects.get(pk=feed_id)
    try:
        posts = fetch_posts(feed.link, feed.link_field)
        published = publish_posts(feed, posts)
        Stat.objects.create(app=Stat.APP_RSS, note=str(feed), count=published)
    except Exception as e:
        logger.error(str(e))
        logger.error(traceback.format_exc())


@celery_app.task
def fetch_and_publish(force=False):
    logger.info('Publishing rss posts...')
    SiteConfig.get_solo().check_maintenance(force)
    publishing_job = group([
        publish_feed.s(feed.id)
        for feed in RssFeed.objects.filter(active=True)
    ])
    publishing_job.apply_async()


@celery_app.task
def delete_old_posts_db():
    stats = {}
    keep = settings.RSS_CLEAN_KEEP
    for feed in RssFeed.objects.all():
        posts = feed.posts
        posts = posts.order_by('-created')[keep:]  # keep latest
        posts_ids = posts.values_list("id", flat=True)  # get only ids
        # get post again because sql-delete can't be used with limit (aka slice)
        posts = Post.objects.filter(pk__in=posts_ids)
        deleted, _ = posts.delete()
        stats[str(feed)] = deleted
        Stat.objects.create(app=Stat.APP_RSS, count=deleted,
                            task=Stat.TASK_CLEAN_UP, note=str(feed))
        logger.info(f'Deleted {deleted} post(s) from feed {feed}.')
    return stats


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **_):
    logger.info('SCHEDULING RSS')
    # publish
    cron = crontab(hour='*', minute='10,40')
    sender.add_periodic_task(cron, fetch_and_publish.s(), name='rss.publishing')
    # clean up
    cron = crontab(hour='*/12', minute='55')
    sender.add_periodic_task(cron, delete_old_posts_db.s(), name='rss.clean_up')
