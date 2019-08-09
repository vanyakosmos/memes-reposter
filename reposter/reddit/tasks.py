import logging
import os
from datetime import datetime, timedelta
from glob import glob
from typing import List

import pytz
import youtube_dl
from celery.schedules import crontab
from django.conf import settings
from django.utils import timezone

from application.celery import app as celery_app
from core.publisher import publish_posts, publish_post
from .filters import apply_filters
from .models import Post, Subreddit

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
        'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
    }
    with youtube_dl.YoutubeDL(options) as ydl:
        links = []
        for post in posts:
            correct_link = 'v.redd.it' in post.url or settings.APP_URL in post.url
            if not (post.video_url and correct_link):
                continue
            link = post.comments
            info = ydl.extract_info(link, download=False)
            video_id = info['id']
            ext = info['ext']

            if info['acodec'] == 'none':
                continue

            file_path = os.path.join(settings.VIDEOS_ROOT, f'{video_id}.{ext}')
            post.video_url = f'{settings.APP_URL}/videos/{video_id}.{ext}'
            post.file_path = file_path
            post.save()
            if not os.path.exists(file_path):
                links.append(post.comments)
        ydl.download(links)


@celery_app.task
def publish_sub(subreddit_id: int, blank: bool):
    logger.debug(f"publish_sub: id={subreddit_id}, blank={blank}")
    subreddit = Subreddit.objects.get(pk=subreddit_id)
    raw_posts = subreddit.get_posts()
    posts = pack_posts(raw_posts, subreddit)
    posts = apply_filters(posts, subreddit)

    if blank:
        for post in posts:
            logger.info(f"Blank publishing: {post!r}")
            post.status = Post.REJECTED
            post.save()
        return

    load_videos(posts)
    for post in posts:
        post.save()
    posts = filter(lambda p: p.status == Post.ACCEPTED, posts)
    posts = [p.normalize() for p in posts]

    subs = subreddit.subs.all()
    publish_posts(subs, posts)


@celery_app.task
def fetch_and_publish(blank=False):
    logger.info('Publishing reddit posts...')
    for subreddit in Subreddit.objects.filter(active=True):
        publish_sub.delay(subreddit.id, blank)


@celery_app.task
def publish_post_task(post_id, post_title: bool):
    try:
        post = Post.objects.select_related().get(id=post_id)
    except Post.DoesNotExist:
        return
    if post.status != Post.ALMOST:
        return
    post.status = Post.ACCEPTED
    post.save()
    load_videos([post])
    p = post.normalize(with_title=post_title)
    subs = post.subreddit.subs.all()
    publish_post(subs, p)


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
