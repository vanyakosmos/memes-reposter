import re
from html import unescape
from pprint import pprint

import requests
from django.core import validators
from django.db import models

from solo.models import SingletonModel

from apps.core.fields import URLField


GIPHY_REGEX = re.compile(r'^https?://(?:media|i)\.giphy\.com/media/(\w+)/giphy\.(?:gif|mp4)$')
GFYCAT_REGEX = re.compile(r'^https?://(?:\w+\.)?gfycat.com/(?:\w+/)*(\w+)(?:\.mp4)?$')
IMGUR_GIF_REGEX = re.compile(r'^(.+)\.gifv?$')
REDDIT_REGEX = re.compile(r'^https?://(www.)?reddit.com/.*$')
TRASH_REGEX = re.compile(r'[^\w\s]')


class RedditConfig(SingletonModel):
    forbidden_keywords = models.TextField(blank=True)
    publish_cron = models.CharField(max_length=200, default='*/30 * * * * *')
    clean_cron = models.CharField(max_length=200, default='0 */12 * * * *')

    @property
    def forbidden_keywords_set(self):
        return set(self.forbidden_keywords.split())


class Subreddit(models.Model):
    name = models.CharField(max_length=200)
    score_limit = models.IntegerField(validators=[validators.MinValueValidator(0)])
    pass_nsfw = models.BooleanField(default=False)
    show_title = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    on_moderation = models.BooleanField(default=False)


class Post(models.Model):
    subreddit = models.ForeignKey(Subreddit, on_delete=models.CASCADE)
    title = models.TextField()
    link = URLField(unique=True)
    reddit_id = models.CharField(max_length=200, unique=True)
    nsfw = models.BooleanField(default=False)

    @property
    def title_terms(self):
        title = self.title.lower()
        title = TRASH_REGEX.sub('', title)
        return title.split()

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, s: str):
        self._score = s

    @property
    def media(self):
        return self._media

    @media.setter
    def media(self, m: dict):
        self._media = m

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
        # pprint(item)
        # print('= ' * 50)
        post = Post(
            subreddit=subreddit,
            title=unescape(item['title']),
            link=re.sub(r'\?.*$', '', item['url']),
            reddit_id=item['id'],
            nsfw=item['over_18'],
        )
        post.score = int(item['score'])
        # post.domain = item['domain']

        result = {
            'type': 'link',
            'url': post.link,
            'text': '',
        }
        domain = item['domain']

        # === IMAGES ===
        if cls._has_ext(item['url'], '.png', '.jpg', '.jpeg'):
            result['type'] = 'photo'
            result['url'] = item['url']
        # imgur single image post
        elif domain in ('imgur.com', 'm.imgur.com'):
            result['url'] = item['url'] + '.png'
            result['type'] = 'photo'

        # === VIDEOS ===
        elif domain == 'gfycat.com':
            result['url'] = cls._get_gfycat_url(item['url'])
            result['type'] = 'video'
        elif domain in ('media.giphy.com', 'i.giphy.com'):
            gif_id = GIPHY_REGEX.findall(item['url'])[0]
            result['url'] = f'https://i.giphy.com/media/{gif_id}/giphy.mp4'
            result['type'] = 'video'
        elif domain == 'i.imgur.com':
            result['url'] = IMGUR_GIF_REGEX.sub('\g<1>.mp4', item['url'])
            result['type'] = 'video'
        elif domain == 'v.redd.it':
            result['type'] = 'video'
            result['url'] = item['url'] + '/DASH_600_K'

        # === TEXTS ===
        elif REDDIT_REGEX.match(item['url']):
            result['type'] = 'text'
            result['text'] = item['selftext']

        post.media = result
        return post
