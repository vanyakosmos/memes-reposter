import logging
from time import sleep
from typing import List

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from telegram import TelegramError, Chat as TGChat
from telegram.error import BadRequest

from core.post import Post
from telegram_app.publisher import publish_post
from .bot import bot

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
        help_text="List of keywords that are forbidden in current chat.",
    )

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
        size = len(posts)
        for i, post in enumerate(posts):
            published = publish_post(self, post)
            sleep(0.5)
            if published:
                logger.info('Published %3d/%d: %s', i + 1, size, repr(post))
            else:
                logger.info('Error %3d/%d: %s', i + 1, size, repr(post))
