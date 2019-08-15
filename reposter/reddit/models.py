import logging
import re
from html import unescape

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models

from .fetcher import get_about, get_posts, get_reddit_url
from .utils import get_photo_url, get_video_url, get_gif_url
from core.fields import URLField
from core.post import Post as NormalPost, Media

NOT_ALPHANUMERIC = re.compile(r'[^\w\s]')
logger = logging.getLogger(__name__)


class Subreddit(models.Model):
    name = models.CharField(
        max_length=255,
        help_text="Subreddit name or search criterion (eg 'popular' or 'all')",
    )
    active = models.BooleanField(default=True)
    score_limit = models.IntegerField(
        validators=[validators.MinValueValidator(0)],
        default=1000,
        help_text="Required score to be send to moderation.",
    )
    score_limit_repost = models.IntegerField(
        validators=[validators.MinValueValidator(0)],
        default=100000,
        help_text="Required score for automatic repost by bot.",
    )
    pass_nsfw = models.BooleanField(default=False)
    show_title = models.BooleanField(default=True)
    forbidden_keywords = ArrayField(models.CharField(max_length=255), default=list, blank=True)

    def __str__(self):
        return f'Subreddit({self.name})'

    @property
    def url(self):
        return get_reddit_url(self.name, api=False)

    @property
    def forbidden_keywords_set(self):
        return set(self.forbidden_keywords)

    def clean(self):
        if self.score_limit > self.score_limit_repost:
            raise ValidationError("Invalid score limits. Score limit for repost should be higher.")

    def get_about(self):
        return get_about(self.name)

    def get_posts(self, limit: int = None):
        limit = limit or settings.REDDIT_POSTS_LIMIT
        return get_posts(self.name, limit)


class PostManager(models.Manager):
    def pending(self):
        return self.filter(status=Post.PENDING)

    def pending_subs(self):
        posts = Post.objects.pending()
        return posts.values_list('subreddit_name', flat=True).distinct()


class Post(models.Model):
    ACCEPTED = 'accepted'
    PENDING = 'pending'
    ALMOST = 'almost'
    REJECTED = 'rejected'
    STATUSES = (
        (ACCEPTED, ACCEPTED),
        (PENDING, PENDING),
        (ALMOST, ALMOST),
        (REJECTED, REJECTED),
    )

    TEXT = 'text'
    LINK = 'link'
    PHOTO = 'photo'
    VIDEO = 'video'
    ANIMATION = 'animation'
    TYPES = (
        (TEXT, TEXT),
        (LINK, LINK),
        (PHOTO, PHOTO),
        (VIDEO, VIDEO),
        (ANIMATION, ANIMATION),
    )

    status = models.CharField(max_length=200, choices=STATUSES, default=ACCEPTED)
    created = models.DateTimeField(auto_now_add=True)

    reddit_id = models.CharField(max_length=200, unique=True)
    subreddit = models.ForeignKey(Subreddit, on_delete=models.CASCADE)
    subreddit_name = models.CharField(max_length=255)
    # meta
    title = models.TextField()
    score = models.IntegerField()
    nsfw = models.BooleanField(default=False)
    comments = URLField(blank=True, null=True)
    # content
    url = URLField(null=True, blank=True)
    type = models.CharField(max_length=50, choices=TYPES, default=TEXT)
    text = models.TextField(null=True, blank=True)
    file_path = models.TextField(null=True, blank=True)
    transcript = models.TextField(null=True, blank=True)

    objects = PostManager()

    def __str__(self):
        return f'Post({self.status}, {self.reddit_id}, {self.title!r})'

    @property
    def tokens(self):
        title = self.title.lower()
        title = NOT_ALPHANUMERIC.sub('', title)
        tokens = title.split()
        if self.transcript:
            transcript = NOT_ALPHANUMERIC.sub('', self.transcript)
            tokens.extend(transcript.split())
        return tokens

    @property
    def comments_short(self):
        return f'https://redd.it/{self.reddit_id}'

    @classmethod
    def get_url(cls, data: dict):
        photo_url = get_photo_url(data)
        video_url = get_video_url(data)
        animation_url = get_gif_url(data)
        if data['selftext']:
            url = None
            type = Post.TEXT
        elif photo_url:
            url = photo_url
            type = Post.PHOTO
        elif video_url:
            url = video_url
            type = Post.VIDEO
        elif animation_url:
            url = animation_url
            type = Post.ANIMATION
        else:
            url = data['url']
            type = Post.LINK
        return url, type

    @classmethod
    def from_dict(cls, data: dict, subreddit: Subreddit):
        url, type = cls.get_url(data)
        return Post(
            reddit_id=data['id'],
            subreddit=subreddit,
            subreddit_name=data['subreddit'],
            # meta
            title=unescape(data['title']),
            score=int(data['score']),
            nsfw=data['over_18'],
            comments='https://reddit.com' + data['permalink'],
            # content
            url=url,
            type=type,
            text=data['selftext']
        )

    def normalize(self, with_title=True):
        if self.type in (Post.ANIMATION, Post.VIDEO, Post.PHOTO):
            media = Media(
                url=self.url,
                video=self.type in (Post.ANIMATION, Post.VIDEO),
                file_path=self.file_path,
            )
            medias = [media]
        else:
            medias = []
        return NormalPost(
            id=f"reddit:{self.reddit_id}",
            url=self.url,
            comments=self.comments,
            title=self.title if with_title else None,
            text=self.text,
            keywords=self.tokens,
            medias=medias,
        )
