import feedparser
from django.core.exceptions import ValidationError
from django.db import models
from telegram import TelegramError

from apps.core.fields import URLField
from memes_reposter import tg_bot


class Channel(models.Model):
    NO_BUTTONS = 'no-buttons'
    LINK_BUTTON = 'link'
    LINK_AND_COMMENTS_BUTTONS = 'link+comments'
    BUTTON_TYPES = (
        (NO_BUTTONS, 'No buttons'),
        (LINK_BUTTON, 'Only link'),
        (LINK_AND_COMMENTS_BUTTONS, 'Link and comments'),
    )

    identifier = models.CharField(max_length=200, null=True, blank=True)
    username = models.CharField(max_length=200, null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    buttons_type = models.CharField(max_length=100, choices=BUTTON_TYPES, default=NO_BUTTONS)
    publish_picture = models.BooleanField(default=False)
    linked_title = models.BooleanField(default=False)
    short_link = models.BooleanField(default=False)
    signature = models.TextField(blank=True)

    @property
    def chat_id(self):
        return self.identifier or '@' + self.username

    @property
    def tg_link(self):
        if self.username:
            return f'https://t.me/{self.username}'
        return ''

    def clean(self):
        # no either id or username should be specified
        if not self.identifier and not self.username:
            raise ValidationError("Identifier or username should be provided for channel.")
        # no access to channel
        try:
            tg_bot.get_chat(chat_id=self.chat_id)
            admins = tg_bot.get_chat_administrators(chat_id=self.chat_id)

            for admin in admins:
                if admin.user.username == tg_bot.username:
                    if not admin.can_post_messages:
                        raise ValidationError("Bot can't post messages.")
                    break
            else:
                raise ValidationError("Bot is not admin.")
        except TelegramError:
            raise ValidationError("Bot doesn't have access to this channel.")

    def __str__(self):
        name = f'<Channel {self.id}>'
        if self.title and self.username:
            name = f"{self.title} ({self.username})"
        elif self.title:
            name = self.title
        elif self.username:
            name = self.username
        return name

    def save(self, refresh_meta=True, **kwargs):
        if refresh_meta:
            # bot = bot or get_bot()
            chat = tg_bot.get_chat(chat_id=self.chat_id)
            self.identifier = chat.id
            self.username = chat.username
            self.title = chat.title
        super(Channel, self).save(**kwargs)


class RssFeed(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    link = models.URLField()
    title = models.CharField(max_length=300, blank=True, null=True)
    link_field = models.CharField(max_length=200, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        name = self.title or self.link
        return f"{self.channel} / {name}"

    def clean(self):
        feed = feedparser.parse(self.link)
        if feed['bozo'] != 0:
            raise ValidationError("Not valid rss link.")

    def save(self, update_title=True, **kwargs):
        if update_title:
            feed = feedparser.parse(self.link)
            self.title = feed['feed']['title']
        super(RssFeed, self).save(**kwargs)

    class Meta:
        unique_together = ('link', 'channel',)


class Post(models.Model):
    title = models.TextField()
    link = URLField()
    feed = models.ForeignKey(RssFeed, on_delete=models.CASCADE, related_name='posts')
    pic_link = URLField(null=True, blank=True)
    comments_link = URLField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def __repr__(self):
        fields = ['title', 'link', 'feed', 'pic_link']
        pairs = [f'{f}={repr(getattr(self, f))}' for f in fields]
        concat = ', '.join(pairs)
        return f'Post({concat})'

    class Meta:
        unique_together = ('link', 'feed',)

    def validate_unique(self, exclude=None):
        if Post.objects.filter(link=self.link, feed__channel=self.feed.channel).exists():
            raise ValidationError('Link but be unique in channel.')
        super(Post, self).validate_unique(exclude)
