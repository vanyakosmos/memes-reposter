import logging
from datetime import timedelta

from celery.schedules import crontab
from django.conf import settings
from django.utils import timezone

from apps.core.errors import ConfigError
from apps.core.models import SiteConfig
from memes_reposter import celery_app
from .fetcher import fetch, populate_albums
from .filters import apply_filters
from .models import ImgurConfig, Post
from .publisher import publish_blank, publish_posts


logger = logging.getLogger(__name__)


def pack_posts(raw_posts):
    posts = [
        Post.from_dict(raw_post)
        for raw_post in raw_posts
    ]
    return posts


@celery_app.task
def fetch_and_publish(force=False, blank=False) -> dict:
    logger.info('Publishing imgur posts...')
    SiteConfig.get_solo().check_maintenance(force)
    imgur_config = ImgurConfig.get_solo()
    if not imgur_config.chat_id:
        raise ConfigError('Nowhere to post. Set up channel in imgur config.')
    client_id = settings.IMGUR_CLIENT_ID
    raw_posts = fetch(client_id, settings.IMGUR_FETCH_LIMIT)
    posts = pack_posts(raw_posts)
    posts = apply_filters(posts, imgur_config)
    populate_albums(posts, client_id, limit=10)
    if blank:
        publish_blank(posts)
    else:
        publish_posts(posts, imgur_config)
    logger.info('Done publishing imgur posts.')
    return {'published': len(posts)}


@celery_app.task
def delete_old_posts():
    time = timezone.now() - timedelta(days=3)
    posts = Post.objects.filter(created__lte=time)
    deleted, _ = posts.delete()
    logger.info(f'Deleted {deleted} post(s).')
    return deleted


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **_):
    logger.info('SCHEDULING IMGUR')
    # publish
    cron = crontab(hour='*', minute='5,35')
    sender.add_periodic_task(cron, fetch_and_publish.s(), name='imgur.publishing')
    # clean up
    cron = crontab(hour='*/12', minute='55')
    sender.add_periodic_task(cron, delete_old_posts.s(), name='imgur.clean_up')
