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
    username = models.CharField(max_length=200, null=True, blank=True)
    chat_id = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.username

    @property
    def forbidden_keywords_set(self):
        return set(self.forbidden_keywords.split())

    def _bot_has_access(self):
        try:
            bot.get_chat(chat_id=self.username)
        except TelegramError:
            raise ValidationError("Bot doesn't have access to this channel.")

    def _bot_id_admin(self):
        admins = bot.get_chat_administrators(chat_id=self.username)
        for admin in admins:
            if admin.user.username == bot.username:
                if not admin.can_post_messages:
                    raise ValidationError("Bot can't post messages.")
                break
        else:
            raise ValidationError("Bot is not admin.")

    def clean(self):
        name = getattr(self, '_username', None)
        if name != self.username:
            self._bot_has_access()
            self._bot_id_admin()
            setattr(self, '_username', self.username)

    def save(self, *args, **kwargs):
        chat = bot.get_chat(chat_id=self.username)
        self.chat_id = chat.id
        return super().save(*args, **kwargs)


class Subreddit(models.Model):
    name = models.CharField(max_length=200)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    low_score_limit = models.IntegerField(
        validators=[validators.MinValueValidator(0)], default=1000)
    score_limit = models.IntegerField(
        validators=[validators.MinValueValidator(0)], default=1000)
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


class Post(models.Model):
    STATUS_ACCEPTED = 'accepted'
    STATUS_PENDING = 'pending'
    STATUS_ALMOST = 'almost'
    STATUS_REJECTED = 'rejected'
    STATUSES = (
        (STATUS_ACCEPTED, STATUS_ACCEPTED),
        (STATUS_PENDING, STATUS_PENDING),
        (STATUS_ALMOST, STATUS_ALMOST),
        (STATUS_REJECTED, STATUS_REJECTED),
    )

    MEDIA_LINK = 'link'
    MEDIA_TEXT = 'text'
    MEDIA_PHOTO = 'photo'
    MEDIA_VIDEO = 'video'
    MEDIA_TYPES = (
        (MEDIA_LINK, MEDIA_LINK),
        (MEDIA_TEXT, MEDIA_TEXT),
        (MEDIA_PHOTO, MEDIA_PHOTO),
        (MEDIA_VIDEO, MEDIA_VIDEO),
    )

    subreddit = models.ForeignKey(Subreddit, on_delete=models.CASCADE)
    title = models.TextField()
    link = URLField(unique=True)
    reddit_id = models.CharField(max_length=200, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=200, choices=STATUSES, default=STATUS_ACCEPTED)

    score = models.IntegerField(null=True)
    media_link = URLField(blank=True, null=True)
    media_type = models.CharField(max_length=200, choices=MEDIA_TYPES, default=MEDIA_LINK)
    text = models.TextField(null=True, blank=True)
    nsfw = models.BooleanField(default=False)
    comments = URLField(blank=True, null=True)

    def __init__(self, *args, **kwargs):
        # self._post_meta = PostMeta()
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f'{self.reddit_id} : {self.title}'

    def __repr__(self):
        fields = ['reddit_id', 'subreddit', 'title',
                  'media_link', 'media_type', 'score']
        pairs = format_field_pairs(self, fields)
        return f'Post({pairs})'

    @property
    def title_terms(self):
        title = self.title.lower()
        title = TRASH_REGEX.sub('', title)
        return title.split()

    def is_not_media(self):
        return self.media_type in (self.MEDIA_LINK, self.MEDIA_TEXT)

    @property
    def comments_short(self):
        return f'https://redd.it/{self.reddit_id}'

    @property
    def comments_full(self):
        auto_link = f'https://reddit.com/r/{self.subreddit.name}/comments/{self.reddit_id}'
        return self.comments or auto_link

    def populate_media(self, item: dict):
        self.title = unescape(item['title'])
        self.link = item['url']
        self.reddit_id = item['id']
        self.comments = 'https://reddit.com' + item['permalink']

        media = get_media(item)
        self.score = int(item['score'])
        self.media_link = media['media']
        self.media_type = media['type']
        self.text = media['text']
        self.nsfw = item['over_18']

    @classmethod
    def from_dict(cls, item: dict, subreddit: Subreddit):
        post = Post(subreddit=subreddit)
        post.populate_media(item)
        return post
