import re
from html import unescape
from typing import List

import requests
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from solo.models import SingletonModel
from telegram import TelegramError

from apps.core.fields import URLField
from memes_reposter.telegram_bot import bot


GIPHY_REGEX = re.compile(r'^https?://(?:media|i)\.giphy\.com/media/(\w+)/giphy\.(?:gif|mp4)$')
GFYCAT_REGEX = re.compile(r'^https?://(?:\w+\.)?gfycat.com/(?:\w+/)*(\w+)(?:\.mp4)?$')
IMGUR_GIF_REGEX = re.compile(r'^(.+)\.gifv?$')
REDDIT_REGEX = re.compile(r'^https?://(www.)?reddit.com/.*$')
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

    @staticmethod
    def _has_ext(file: str, *exts):
        return any([file.endswith(ext) for ext in exts])

    @staticmethod
    def _get_gfycat_url(gif_url):
        api_url = GFYCAT_REGEX.sub(r'https://api.gfycat.com/v1/gfycats/\g<1>', gif_url)
        res = requests.get(api_url)
        item = res.json()
        url = item['gfyItem']['mp4Url']
        return url

    @classmethod
    def from_dict(cls, item: dict, subreddit: Subreddit):
        post = Post(
            subreddit=subreddit,
            title=unescape(item['title']),
            link=re.sub(r'\?.*$', '', item['url']),
            reddit_id=item['id'],
            nsfw=item['over_18'],
        )
        post.meta.score = int(item['score'])
        post.meta.media_link = post.link
        domain = item['domain']

        # === IMAGES ===
        if cls._has_ext(item['url'], '.png', '.jpg', '.jpeg'):
            post.meta.type = 'photo'
            post.meta.media_link = item['url']
        # imgur single image post
        elif domain in ('imgur.com', 'm.imgur.com'):
            post.meta.media_link = item['url'] + '.png'
            post.meta.type = 'photo'

        # === VIDEOS ===
        elif domain == 'gfycat.com':
            post.meta.media_link = cls._get_gfycat_url(item['url'])
            post.meta.type = 'video'
        elif domain in ('media.giphy.com', 'i.giphy.com'):
            gif_id = GIPHY_REGEX.findall(item['url'])[0]
            post.meta.media_link = f'https://i.giphy.com/media/{gif_id}/giphy.mp4'
            post.meta.type = 'video'
        elif domain == 'i.imgur.com':
            post.meta.media_link = IMGUR_GIF_REGEX.sub('\g<1>.mp4', item['url'])
            post.meta.type = 'video'
        elif domain == 'v.redd.it':
            post.meta.type = 'video'
            post.meta.media_link = item['url'] + '/DASH_600_K'

        # === TEXTS ===
        elif REDDIT_REGEX.match(item['url']):
            post.meta.type = 'text'
            post.meta.text = item['selftext']
        return post
