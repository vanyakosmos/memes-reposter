import logging
from typing import List

from .post import Post, restore_from_raw
from .models import Subscription
from application.celery import app as celery_app
from telegram_app.models import Chat

logger = logging.getLogger(__name__)


@celery_app.task
def publish_into_telegram(chat_id, raw_posts: List[tuple]):
    chat = Chat.objects.get(id=chat_id)
    posts = [restore_from_raw(p) for p in raw_posts]
    chat.publish(posts)


def publish_posts(subs: List[Subscription], posts: List[Post]):
    if not posts:
        logger.debug("no posts to publish")
        return
    for chat in Chat.objects.filter(subs__in=subs).distinct():
        publish_into_telegram.delay(chat.id, posts)


def publish_post(subs: List[Subscription], post: Post):
    publish_posts(subs, [post])
