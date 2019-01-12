import re
from html import unescape

from django.core import validators
from django.db import models
from solo.models import SingletonModel

from apps.core.fields import URLField
from apps.core.models import Subscription
from apps.core.utils import format_object_repr
from apps.reddit.utils import get_media


class RedditConfig(SingletonModel):
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return "Reddit Configuration"

    def __repr__(self):
        return format_object_repr(self, ['enabled'])

    class Meta:
        verbose_name = "Reddit Configuration"
        verbose_name_plural = "Reddit Configuration"


class Subreddit(models.Model):
    subscriptions = models.ManyToManyField(
        Subscription,
        related_name='subreddits',
        blank=True,
        help_text="List of subscriptions that will be notified about subreddit updates.",
    )
    name = models.CharField(max_length=255, help_text="Name of subreddit. W/o /r/.")
    low_score_limit = models.IntegerField(
        validators=[validators.MinValueValidator(0)],
        default=1000,
        help_text="After exceeding this limit posts will be send to moderation.",
    )
    score_limit = models.IntegerField(
        validators=[validators.MinValueValidator(0)],
        default=1000,
        help_text="After exceeding this limit posts will be published.",
    )
    pass_nsfw = models.BooleanField(
        default=False, help_text="Allow to post NSFW content."
    )
    show_title = models.BooleanField(
        default=True, help_text="Drop title if it is useless."
    )
    enabled = models.BooleanField(default=True)
    on_moderation = models.BooleanField(default=True)
    forbidden_keywords = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


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
    subreddit_name = models.CharField(max_length=255)
    reddit_id = models.CharField(max_length=200, unique=True)
    title = models.TextField()
    url = URLField()
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=200, choices=STATUSES, default=STATUS_ACCEPTED)
    score = models.IntegerField(null=True)
    source_url = URLField(blank=True, null=True)
    type = models.CharField(max_length=200, choices=MEDIA_TYPES, default=MEDIA_LINK)
    text = models.TextField(null=True, blank=True)
    nsfw = models.BooleanField(default=False)
    comments = URLField(blank=True, null=True)
    num_comments = models.IntegerField(null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f'{self.reddit_id}: {self.title}'

    def __repr__(self):
        return format_object_repr(
            self,
            ('reddit_id', 'subreddit', 'title', 'media_link', 'media_type', 'score'),
        )

    @property
    def title_terms(self):
        title = self.title.lower()
        title = re.sub(r'[^\w\s]', '', title)
        return title.split()

    @property
    def not_media(self):
        return self.type in (self.MEDIA_LINK, self.MEDIA_TEXT)

    @property
    def comments_short(self):
        return f'https://redd.it/{self.reddit_id}'

    @property
    def comments_full(self):
        return f'https://reddit.com/r/{self.subreddit_name}/comments/{self.reddit_id}'

    def populate_media(self, item: dict):
        self.subreddit_name = item['subreddit']
        self.title = unescape(item['title'])
        self.url = item['url']
        self.reddit_id = item['id']
        self.comments = 'https://reddit.com' + item['permalink']
        self.nsfw = item['over_18']
        self.score = int(item['score'])

        media = get_media(item)
        self.source_url = media['media']
        self.type = media['type']
        self.text = media['text']

    @classmethod
    def from_dict(cls, item: dict, subreddit: Subreddit):
        post = Post(subreddit=subreddit)
        post.populate_media(item)
        return post
