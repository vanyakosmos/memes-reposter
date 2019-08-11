import logging

from django.conf import settings

from application.celery import app as celery_app
from core.publisher import publish_posts
from . import fetcher
from .models import Post, RssFeed

logger = logging.getLogger(__name__)


def filter_posts(posts):
    return [p for p in posts if not Post.objects.filter(feed=p.feed, url=p.url).exists()]


@celery_app.task
def publish_feed(feed_id: int, blank: bool):
    feed = RssFeed.objects.get(pk=feed_id)
    try:
        posts = fetcher.fetch_posts(feed)
    except fetcher.FeedException as e:
        logger.exception(str(e))
        return
    posts = filter_posts(posts)
    logger.debug(f"posts: {posts}")
    for p in posts:
        p.save()
    if blank:
        return
    posts = [p.normalize() for p in posts]
    subs = feed.subs.all()
    publish_posts(subs, posts)


@celery_app.task
def fetch_and_publish(blank=False):
    logger.info('Publishing rss posts...')
    for feed in RssFeed.objects.filter(active=True):
        publish_feed.delay(feed.id, blank)


@celery_app.task
def delete_old_posts(keep=None):
    stats = {}
    keep = keep or settings.RSS_CLEAN_KEEP
    for feed in RssFeed.objects.all():
        posts = feed.posts
        posts = posts.order_by('-created')[keep:]  # keep latest
        posts_ids = posts.values_list("id", flat=True)  # get only ids
        # get post again because sql-delete can't be used with limit (aka slice)
        posts = Post.objects.filter(pk__in=posts_ids)
        deleted, _ = posts.delete()
        stats[str(feed)] = deleted
        logger.info(f'Deleted {deleted} post(s) from feed {feed}.')
    return stats
