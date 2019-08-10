from django.db import models

from reddit.models import Subreddit
from telegram_app.models import Chat
from rss.models import RssFeed
from imgur.models import ImgurConfig


class Related(models.ManyToManyField):
    def __init__(self, to, *args, **kwargs):
        kwargs.setdefault('related_name', 'subs')
        kwargs.setdefault('blank', True)
        super().__init__(to, *args, **kwargs)


class Subscription(models.Model):
    name = models.CharField(max_length=255)
    # sources
    subreddits = Related(Subreddit)
    rss_feeds = Related(RssFeed)
    imgur_configs = Related(ImgurConfig)
    # targets
    telegram_chats = Related(Chat)

    def __str__(self):
        return self.name
