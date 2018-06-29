import re
from html import unescape
from typing import List

from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from telegram import TelegramError

from apps.core.fields import URLField
from apps.reddit.utils import get_media
from memes_reposter.telegram_bot import bot


TRASH_REGEX = re.compile(r'[^\w\s]')


class Channel(models.Model):
    forbidden_keywords = models.TextField(blank=True)
    publish_cron = models.CharField(max_length=200, default='*/30 * * * * *')
    clean_cron = models.CharField(max_length=200, default='0 */12 * * * *')
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    @property
    def forbidden_keywords_set(self):
        return set(self.forbidden_keywords.split())

    def _bot_id_admin(self, admins):
        for admin in admins:
            if admin.user.username == bot.username:
                if not admin.can_post_messages:
                    raise ValidationError("Bot can't post messages.")
                break
        else:
            raise ValidationError("Bot is not admin.")

    def clean(self):
        name = getattr(self, '_name', None)
        if name != self.name:
            try:
                bot.get_chat(chat_id=self.name)
                admins = bot.get_chat_administrators(chat_id=self.name)
                self._bot_id_admin(admins)
            except TelegramError:
                raise ValidationError("Bot doesn't have access to this channel.")
            setattr(self, '_name', self.name)


class Subreddit(models.Model):
    name = models.CharField(max_length=200)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    score_limit = models.IntegerField(validators=[validators.MinValueValidator(0)])
    pass_nsfw = models.BooleanField(default=False)
    show_title = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    on_moderation = models.BooleanField(default=False)
    forbidden_keywords = models.TextField(blank=True)

    def __str__(self):
        return self.name

    @property
    def forbidden_keywords_set(self):
        keywords = set(self.forbidden_keywords.split())
        return keywords | self.channel.forbidden_keywords_set


def format_field_pairs(obj, fields: List[str]):
    return ', '.join([
        f'{field}="{getattr(obj, field, None)}"'
        for field in fields
    ])


class PostMeta(object):
    def __init__(self):
        self.score = None  # type: int
        self.media_link = None  # type: str
        self.type = None  # type: str
        self.text = None  # type: str

    def __repr__(self):
        fields = ['score', 'media_link', 'type']
        pairs = format_field_pairs(self, fields)
        return f'PostMeta({pairs})'


class Post(models.Model):
    subreddit = models.ForeignKey(Subreddit, on_delete=models.CASCADE)
    title = models.TextField()
    link = URLField(unique=True)
    reddit_id = models.CharField(max_length=200, unique=True)
    nsfw = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        self._post_meta = PostMeta()
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.title

    def __repr__(self):
        fields = ['reddit_id', 'subreddit', 'title', 'link']
        pairs = format_field_pairs(self, fields)
        return f'Post({pairs}, meta={repr(self.meta)})'

    @property
    def title_terms(self):
        title = self.title.lower()
        title = TRASH_REGEX.sub('', title)
        return title.split()

    @property
    def meta(self):
        return self._post_meta

    @property
    def comments(self):
        return f'https://redd.it/{self.reddit_id}'

    @property
    def comments_full(self):
        return f'https://reddit.com/r/{self.subreddit.name}/comments/{self.reddit_id}'

    @classmethod
    def from_dict(cls, item: dict, subreddit: Subreddit):
        post = Post(
            subreddit=subreddit,
            title=unescape(item['title']),
            link=re.sub(r'\?.*$', '', item['url']),
            reddit_id=item['id'],
            nsfw=item['over_18'],
        )
        media = get_media(item)
        post.meta.score = int(item['score'])
        post.meta.media_link = media['media']
        post.meta.type = media['type']
        post.meta.text = media['text']
        return post
