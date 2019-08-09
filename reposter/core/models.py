from django.db import models

from reddit.models import Subreddit
from telegram_app.models import Chat


class Subscription(models.Model):
    name = models.CharField(max_length=255)
    # sources
    subreddits = models.ManyToManyField(Subreddit, related_name='subs', blank=True)
    # targets
    telegram_chats = models.ManyToManyField(Chat, related_name='subs', blank=True)

    def __str__(self):
        return self.name
