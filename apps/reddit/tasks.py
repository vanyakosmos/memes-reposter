import logging
import os
from datetime import datetime, timedelta
from glob import glob
from typing import List

import pytz
import youtube_dl
from celery import group
from django.conf import settings
from django.utils import timezone

from apps.core.models import SiteConfig
from apps.tgapp.publishers.reddit import publish_post
from reposter import celery_app
from .fetcher import fetch
from .filters import apply_filters
from .models import Post, RedditConfig, Subreddit


logger = logging.getLogger(__name__)


@celery_app.task
def publish_posts_task(force=False, blank=False):
    if skip_publishing(force):
        logger.info('Skip publishing.')
        return False

    logger.info(f'Publishing reddit posts (force={force}, blank={blank})...')
    publishing_job = group(
        [
            publish_subreddit_task.si(subreddit.id, blank)
            for subreddit in Subreddit.objects.filter(enabled=True)
        ]
    )
    publishing_job.apply_async()
    return True


@celery_app.task
def publish_subreddit_task(subreddit_id, blank):
    subreddit = Subreddit.objects.get(id=subreddit_id)
    posts = fetch(subreddit.name, limit=settings.REDDIT_FETCH_SIZE)
    posts = pack_posts(posts, subreddit)
    # todo: filter in context of concrete channel
    posts = apply_filters(posts, subreddit)
    load_videos(posts)

    processed_channels = set()
    for subscription in subreddit.subscriptions.all():
        for channel in subscription.tg_channels.all():
            if channel in processed_channels:
                continue
            for post in posts:
                post.save()
                if post.status != Post.STATUS_ACCEPTED or blank:
                    continue
                published = publish_post(post, channel, sleep_time=0.5)
                mark = '✅' if published else '❌'
                logger.debug(f"{mark}  > {post}")


def skip_publishing(force=False):
    return not force and (
        not SiteConfig.get_solo().enabled or not RedditConfig.get_solo().enabled
    )


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
            correct_link = ('v.redd.it' in post.source_url) or (
                settings.THIS_HOST in post.source_url
            )
            if post.type == 'video' and correct_link:
                link = post.comments_full
                info = ydl.extract_info(link, download=False)
                video_id = info['id']
                ext = info['ext']

                if info['acodec'] == 'none':
                    continue

                file_path = os.path.join(settings.VIDEOS_ROOT, f'{video_id}.{ext}')
                post.source_url = f'{settings.THIS_HOST}/videos/{video_id}.{ext}'
                post.file_path = file_path
                if not os.path.exists(file_path):
                    links.append(post.comments_full)
        ydl.download(links)


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
    load_videos([post])
    subreddit = post.subreddit
    for subscription in subreddit.subscriptions.all():
        for channel in subscription.tg_channels.all():
            publish_post(post, channel, post_title)


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
