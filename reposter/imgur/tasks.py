import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from application.celery import app as celery_app
from core.publisher import publish_posts
from .fetcher import fetch, populate_albums
from .filters import apply_filters
from .models import ImgurConfig, Post

logger = logging.getLogger(__name__)


@celery_app.task
def publish_imgur_posts(imgur_id, blank: bool):
    imgur_config = ImgurConfig.objects.get(id=imgur_id)
    raw_posts = fetch(settings.IMGUR_CLIENT_ID, settings.IMGUR_FETCH_LIMIT)
    posts = [Post.from_dict(raw_post, imgur_config) for raw_post in raw_posts]
    posts = apply_filters(posts)
    populate_albums(posts, settings.IMGUR_CLIENT_ID, limit=10)
    for post in posts:
        post.save()
    if blank:
        return
    posts = [p.normalize() for p in posts]
    subs = imgur_config.subs.all()
    publish_posts(subs, posts)


@celery_app.task
def fetch_and_publish(blank=False):
    logger.info('Publishing imgur posts...')
    for imgur in ImgurConfig.objects.filter(active=True):
        publish_imgur_posts.delay(imgur.id, blank)


@celery_app.task
def delete_old_posts(days):
    days = days or settings.IMGUR_DELETE_OLD_DAYS
    time = timezone.now() - timedelta(days=days)
    posts = Post.objects.filter(created__lte=time)
    deleted, _ = posts.delete()
    logger.info(f'Deleted {deleted} post(s).')
    return deleted
