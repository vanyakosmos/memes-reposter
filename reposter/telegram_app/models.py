import logging
from time import sleep
from typing import List

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from telegram import Chat as TGChat, TelegramError
from telegram.error import BadRequest

from core.post import Post
from .bot import bot
from .filters import filters_posts
from .publisher import publish_post

logger = logging.getLogger(__name__)


def get_chat_title(chat: TGChat):
    if chat.title:
        return chat.title
    elif chat.first_name and chat.last_name:
        return f"{chat.first_name} {chat.last_name}"
    elif chat.first_name:
        return chat.first_name


class Chat(models.Model):
    telegram_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="Telegram ID.",
    )
    username = models.CharField(
        max_length=255,
        help_text="Username of telegram ID.",
    )
    type = models.CharField(
        max_length=100,
        help_text="Type of chat (eg private, supergroup, etc).",
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Group/channel title or user's full name.",
    )
    forbidden_keywords = ArrayField(
        models.CharField(max_length=255),
        default=list,
        blank=True,
        help_text="List of keywords that are forbidden in current chat.",
    )

    def __str__(self):
        return f"Chat({self.telegram_id}, {self.type}, {self.username}, {self.title!r})"

    @property
    def chat_id(self):
        try:
            username = int(self.username)
        except ValueError:
            username = f'@{self.username}'
        return self.telegram_id or username

    @property
    def forbidden_keywords_set(self):
        return set(self.forbidden_keywords)

    def update_from_telegram(self, chat: TGChat = None):
        chat = chat or bot.get_chat(chat_id=self.chat_id)
        self.telegram_id = chat.id
        self.type = chat.type
        self.username = chat.username
        self.title = get_chat_title(chat)

    def bot_has_access(self):
        try:
            bot.get_chat(chat_id=self.chat_id)
        except TelegramError as e:
            logger.debug(e)
            raise ValidationError(str(e))

    def bot_is_admin(self):
        if not self.type:
            self.type = bot.get_chat(chat_id=self.chat_id).type
        if self.type == TGChat.PRIVATE:
            return
        try:
            admins = bot.get_chat_administrators(chat_id=self.chat_id)
        except BadRequest as e:
            logger.debug(e)
            raise ValidationError(str(e))
        for admin in admins:
            if admin.user.username == bot.username:
                logger.debug(admin)
                if self.type == TGChat.CHANNEL and not admin.can_post_messages:
                    raise ValidationError("Bot can't post messages in this channel.")
                break
        else:
            raise ValidationError("Bot is not admin.")

    def clean(self):
        self.bot_has_access()
        self.bot_is_admin()

        self.update_from_telegram()
        setattr(self, '_updated', True)
        chat = Chat.objects.filter(telegram_id=self.telegram_id).first()
        if chat and self.id != chat.id:
            url = reverse('admin:telegram_app_chat_change', args=(chat.id,))
            raise ValidationError(
                mark_safe(f'<a href="{url}">Chat with this ID already exists.</a>')
            )

    def save(self, *args, **kwargs):
        if not getattr(self, '_updated', False):
            logger.debug("update in save()")
            self.update_from_telegram()
        return super().save(*args, **kwargs)

    def publish(self, posts: List[Post]):
        logger.debug(f"if chat: {self}")
        logger.debug(f"got {len(posts)} posts")
        posts = filters_posts(self, posts)
        logger.debug(f"{len(posts)} posts after filter")
        size = len(posts)
        for i, post in enumerate(posts):
            logger.debug(repr(post))
            qs = Q(identifier=post.id)
            if post.url:
                qs |= Q(url=post.url)
            for m in post.medias:
                qs |= Q(url=m.url)
            if Message.objects.filter(chat=self).filter(qs).exists():
                logger.debug(f"Already in the chat: {post}")
                continue
            msg = publish_post(self, post)
            if msg:
                Message.objects.create(
                    chat=self,
                    message_id=msg.message_id,
                    identifier=post.id,
                    url=post.url,
                    text=post.text,
                )
                logger.debug('Published %3d/%d: %s', i + 1, size)
            else:
                logger.debug('Error %3d/%d: %s', i + 1, size)
            sleep(0.5)  # prevent burst throttling


# todo: allow to admin through admin
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    message_id = models.CharField(max_length=255)
    identifier = models.CharField(
        max_length=255,
        help_text=(
            "Message ID in specific chat. Similar to message_id "
            "but determined before posting and required for filtration."
        )
    )
    url = models.CharField(max_length=255, null=True, blank=True)
    photo_url = models.CharField(max_length=255, null=True, blank=True)
    video_url = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('identifier', 'chat')
