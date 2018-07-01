from collections import namedtuple
from typing import List

from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from solo.models import SingletonModel
from telegram import TelegramError

from memes_reposter.telegram_bot import bot


class ImgurConfig(SingletonModel):
    score_limit = models.IntegerField(default=1000,
                                      validators=[validators.MinValueValidator(0)])
    good_tags = models.TextField(blank=True,
                                 help_text="List of good tags. Should be separated with comma.")
    bad_tags = models.TextField(blank=True,
                                help_text="List of bad tags. Should be separated with comma.")
    exclude_mode = models.BooleanField(default=True,
                                       help_text="If true then posts with bad tags will be filtered out. "
                                                 "Otherwise only posts from with good tags will pass the filter.")
    channel_username = models.CharField(max_length=200, null=True)
    chat_id = models.BigIntegerField(null=True, blank=True)

    def _bot_has_access(self):
        try:
            bot.get_chat(chat_id=self.channel_username)
        except TelegramError:
            raise ValidationError("Bot doesn't have access to this channel.")

    def _bot_id_admin(self):
        admins = bot.get_chat_administrators(chat_id=self.channel_username)
        for admin in admins:
            if admin.user.username == bot.username:
                if not admin.can_post_messages:
                    raise ValidationError("Bot can't post messages.")
                break
        else:
            raise ValidationError("Bot is not admin.")

    @staticmethod
    def _tags_to_set(tags_string: str):
        if tags_string:
            return {
                '_'.join(tag.strip().split())
                for tag in tags_string.split(',')
            }
        return set()

    @property
    def bad_tags_set(self):
        return self._tags_to_set(self.bad_tags)

    @property
    def good_tags_set(self):
        return self._tags_to_set(self.good_tags)

    def clean(self):
        self._bot_has_access()
        self._bot_id_admin()

    def save(self, *args, **kwargs):
        if self.channel_username:
            chat = bot.get_chat(chat_id=self.channel_username)
            self.chat_id = chat.id
        return super().save(*args, **kwargs)


Media = namedtuple('Media', 'link desc animated')
PostMeta = namedtuple('PostMeta', 'desc score')


class Post(models.Model):
    imgur_id = models.CharField(max_length=200)
    title = models.TextField()
    is_album = models.BooleanField()
    tags = models.TextField()
    images_links = models.TextField()
    images_count = models.IntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        self._post_meta = None  # type: PostMeta
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
    def meta(self):
        return self._post_meta

    @property
    def medias(self):
        return self._medias

    @medias.setter
    def medias(self, images: list):
        self._medias = [
            Media(
                link=item['mp4'] if item['animated'] else item['link'],
                animated=item['animated'],
                desc=item['description'],
            )
            for item in images
        ]
        self.images_links = ', '.join([i.link for i in self._medias])

    @property
    def is_single(self):
        return not self.is_album or self.images_count == 1

    @property
    def tags_set(self):
        if self.tags:
            return set(self.tags.split(', '))
        return set()

    @classmethod
    def from_dict(cls, item: dict):
        post = Post(
            imgur_id=item['id'],
            title=item['title'],
            is_album=item['is_album'],
            tags=', '.join([t['name'] for t in item['tags']]),
            images_count=item.get('images_count', 1),
        )
        if item['is_album']:
            post.medias = item['images']
        else:
            post.medias = [item]
        post._post_meta = PostMeta(
            desc=item['description'],
            score=item['score'],
        )
        return post
