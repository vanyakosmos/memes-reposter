import logging
import os
from datetime import datetime, timedelta
from glob import glob
from typing import List

import pytz
import youtube_dl
from celery import chord
from celery.schedules import crontab
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from apps.core.models import SiteConfig
from apps.core.utils import notify_admins
from memes_reposter.celery import app as celery_app
from .fetcher import fetch
from .filters import apply_filters
from .models import Channel, Post, Subreddit
from .publisher import publish_blank, publish_post, publish_posts


logger = logging.getLogger(__name__)


def pack_posts(raw_posts, subreddit: Subreddit):
    posts = []
    for raw_post in raw_posts:
        try:
            post = Post.from_dict(raw_post, subreddit)
            posts.append(post)
        except Exception as e:
            logger.exception(e)
    return posts


def load_videos(posts: List[Post]):
    options = {
        'outtmpl': os.path.join(settings.VIDEOS_ROOT, '%(id)s.%(ext)s'),
    }
    with youtube_dl.YoutubeDL(options) as ydl:
        links = []
        for post in posts:
            if post.media_type == 'video' and 'v.redd.it' in post.media_link:
                link = post.comments_full
                info = ydl.extract_info(link, download=False)
                video_id = info['id']
                ext = info['ext']
                post.media_link = f'{settings.THIS_HOST}/videos/{video_id}.{ext}'
                post.file_path = os.path.join(settings.VIDEOS_ROOT, f'{video_id}.{ext}')
                links.append(post.comments_full)

        ydl.download(links)


@celery_app.task
def publish_sub(subreddit_id: int, blank: bool):
    subreddit = Subreddit.objects.get(pk=subreddit_id)
    raw_posts = fetch(subreddit.name, limit=settings.REDDIT_FETCH_SIZE)
    posts = pack_posts(raw_posts, subreddit)
    posts = apply_filters(posts, subreddit)
    try:
        load_videos(posts)
    except Exception as e:
        logger.error(e)
    if blank:
        publish_blank(posts)
    else:
        publish_posts(posts)


@celery_app.task
def fetch_and_publish(force=False, blank=False):
    logger.info('Publishing reddit posts...')
    SiteConfig.get_solo().check_maintenance(force)

    jobs = []
    for channel in Channel.objects.all():
        subs = channel.subreddit_set.filter(active=True)
        for subreddit in subs:
            job_sig = publish_sub.s(subreddit.id, blank)
            jobs.append(job_sig)
    publishing_job = chord(jobs, notify_admins_task.si())
    publishing_job.apply_async()


@celery_app.task
def notify_admins_task():
    pending = Post.objects.filter(status=Post.STATUS_PENDING).count()
    if pending > 0:
        s = 'post is' if pending == 1 else 'posts are'
        url = '/'.join([settings.THIS_HOST, reverse('reddit:index')[1:]])
        notify_admins(f"{pending} {s} on moderation.\n{url}")


@celery_app.task
def publish_post_task(post_id, post_title: bool):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return
    if post.status != Post.STATUS_ALMOST:
        return
    post.status = Post.STATUS_ACCEPTED
    post.save()
    publish_post(post, post_title)


@celery_app.task
def delete_old_posts():
    time = timezone.now() - timedelta(days=3)
    posts = Post.objects.filter(created__lte=time)
    deleted, _ = posts.delete()
    logger.info(f'Deleted {deleted} post(s).')
    # delete files
    for file_path in glob(os.path.join('videos', '*')):
        t = os.stat(file_path).st_ctime
        t = datetime.utcfromtimestamp(t).replace(tzinfo=pytz.utc)
        if t < time:
            os.remove(file_path)
            logger.info(f'Deleted {file_path}.')
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
