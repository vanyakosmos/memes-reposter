import logging
from datetime import timedelta

from celery import group
from celery.schedules import crontab
from django.conf import settings
from django.utils import timezone

from apps.core.models import SiteConfig
from memes_reposter.celery import app as celery_app
from .fetcher import fetch
from .filters import apply_filters
from .models import Channel, Post, Subreddit
from .publisher import publish_blank, publish_posts


logger = logging.getLogger(__name__)


def pack_posts(raw_posts, subreddit: Subreddit):
    posts = []
    for raw_post in raw_posts:
        try:
            posts.append(Post.from_dict(raw_post, subreddit))
        except Exception as e:
            logger.error(e)
    return posts


@celery_app.task
def publish_sub(subreddit_id: int, blank: bool):
    subreddit = Subreddit.objects.get(pk=subreddit_id)
    channel = subreddit.channel
    raw_posts = fetch(subreddit.name, limit=settings.REDDIT_FETCH_SIZE)
    posts = pack_posts(raw_posts, subreddit)
    posts = apply_filters(posts, subreddit)
    if blank:
        publish_blank(posts)
    else:
        publish_posts(posts, subreddit)
    key = f'{channel.username} > {subreddit.name}'
    return key, len(posts)


@celery_app.task
def fetch_and_publish(force=False, blank=False, wait=False) -> dict:
    logger.info('Publishing reddit posts...')
    SiteConfig.get_solo().check_maintenance(force)

    jobs = []
    for channel in Channel.objects.all():
        subs = channel.subreddit_set.filter(active=True)
        for subreddit in subs:
            job_sig = publish_sub.s(subreddit.id, blank)
            jobs.append(job_sig)
    publishing_job = group(jobs)
    job_res = publishing_job.apply_async()

    if wait:
        results = job_res.get()
        stats = dict(results)
        logger.info('Done publishing reddit posts.')
        return stats


@celery_app.task
def delete_old_posts():
    time = timezone.now() - timedelta(days=3)
    posts = Post.objects.filter(created__lte=time)
    deleted, _ = posts.delete()
    logger.info(f'Deleted {deleted} post(s).')
    return deleted


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **_):
    logger.info('SCHEDULING REDDIT')
    # publish
    fetch_crontab = crontab(hour='*', minute='0,30')
    sender.add_periodic_task(fetch_crontab, fetch_and_publish.s(), name='reddit.publishing')
    # clean up
    clean_crontab = crontab(hour='*/12', minute='55')
    sender.add_periodic_task(clean_crontab, delete_old_posts.s(), name='reddit.clean_up')
