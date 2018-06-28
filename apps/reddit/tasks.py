import logging
from datetime import timedelta

from celery.schedules import crontab
from django.utils import timezone

from memes_reposter.celery import app as celery_app
from .fetcher import fetch
from .filters import apply_filters
from .models import Post, Subreddit
from .publisher import publish_posts


logger = logging.getLogger(__name__)


def pack_posts(raw_posts, subreddit: Subreddit):
    posts = [
        Post.from_dict(raw_post, subreddit)
        for raw_post in raw_posts
    ]
    return posts


@celery_app.task
def fetch_and_publish():
    stats = {}
    for subreddit in Subreddit.objects.filter(active=True):
        raw_posts = fetch(subreddit.name, limit=10)
        posts = pack_posts(raw_posts, subreddit)
        posts = apply_filters(posts, subreddit)
        publish_posts(posts)
        stats[subreddit.name] = len(posts)
    return stats


@celery_app.task
def delete_old_posts():
    time = timezone.now() - timedelta(days=7)
    posts = Post.objects.filter(created__lte=time)
    deleted, _ = posts.delete()
    logger.info(f'Deleted {deleted} post(s).')
    return deleted


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **_):
    logger.info('SCHEDULING')
    fetch_crontab = crontab(hour='*', minute='30')
    sender.add_periodic_task(fetch_crontab, fetch_and_publish.s(), name='fetch and publish')

    clean_crontab = crontab(hour='12', minute='0')
    sender.add_periodic_task(clean_crontab, delete_old_posts.s(), name='delete old posts')
