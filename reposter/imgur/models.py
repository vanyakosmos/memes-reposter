from typing import List

from django.contrib.postgres.fields import ArrayField, JSONField
from django.core import validators
from django.db import models

from core.post import Post as NormalPost, Media


class ImgurConfig(models.Model):
    score_limit = models.IntegerField(
        default=1000,
        validators=[validators.MinValueValidator(0)],
    )
    allow_albums = models.BooleanField(default=True)
    good_tags = models.TextField(
        blank=True,
        help_text="List of good tags. Should be separated with comma.",
    )
    bad_tags = models.TextField(
        blank=True,
        help_text="List of bad tags. Should be separated with comma.",
    )
    exclude_mode = models.BooleanField(
        default=True,
        help_text=(
            "If true then posts with bad tags will be filtered out. "
            "Otherwise only posts from with good tags will pass the filter."
        ),
    )
    active = models.BooleanField(default=True)

    @staticmethod
    def _tags_to_set(tags_string: str):
        if tags_string:
            return {'_'.join(tag.strip().split()) for tag in tags_string.split(',')}
        return set()

    @property
    def bad_tags_set(self):
        return self._tags_to_set(self.bad_tags)

    @property
    def good_tags_set(self):
        return self._tags_to_set(self.good_tags)


class Post(models.Model):
    config = models.ForeignKey(ImgurConfig, on_delete=models.CASCADE)
    imgur_id = models.CharField(max_length=200)
    title = models.TextField()
    description = models.TextField(null=True, blank=True)
    score = models.IntegerField()
    is_album = models.BooleanField()
    tags = ArrayField(models.CharField(max_length=255), default=list, blank=True)
    media_data = JSONField(default=list, blank=True)
    images_count = models.IntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        self._medias = []  # type: List[Media]
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f'{self.imgur_id} : {self.title}'

    def __repr__(self):
        return f'Post(title={repr(self.title)}, link={repr(self.link)}, is_single={self.is_album})'

    @property
    def link(self):
        base = 'https://imgur.com/'
        if self.is_album:
            base += 'a/'
        return base + self.imgur_id

    @property
    def medias(self):
        return self._medias

    @medias.setter
    def medias(self, images: list):
        self._medias = [
            Media(
                url=data['mp4'] if data['animated'] else data['link'],
                video=data['animated'],
                caption=data['description'],
            ) for data in images
        ]
        self.media_data = self._medias

    @property
    def is_single(self):
        return not self.is_album or self.images_count == 1

    @property
    def tags_set(self):
        return set(self.tags)

    @classmethod
    def from_dict(cls, data: dict, imgur: ImgurConfig):
        post = Post(
            config=imgur,
            imgur_id=data['id'],
            title=data['title'],
            description=data['description'],
            score=data['score'],
            is_album=data['is_album'],
            tags=[t['name'] for t in data['tags']],
            images_count=data.get('images_count', 1),
        )
        if data['is_album']:
            post.medias = data['images']
        else:
            post.medias = [data]
        return post

    def normalize(self):
        return NormalPost(
            id=f"imgur:{self.id}",
            title=self.title,
            description=self.description,
            url=self.link,
            text=None,
            comments=self.link,
            medias=self.medias,
        )
