from typing import List

from .post import Post
from .models import Subscription
from telegram_app.models import Chat


def publish_posts(subs: List[Subscription], posts: List[Post]):
    for chat in Chat.objects.filter(subs__in=subs).distinct():
        chat.publish(posts)


def publish_post(subs: List[Subscription], post: Post):
    publish_posts(subs, [post])
