import uuid

from django.core.exceptions import ValidationError
from django.db import models
from telegram import TelegramError

from apps.core.models import Subscription
from .bot import bot


class TelegramChannel(models.Model):
    name = models.TextField(
        null=True, blank=True, help_text="Human friendly name of channel."
    )
    username = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Channel username, should start with @.",
    )
    chat_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Telegram chat id of channel, can be omitted if username is specified.",
    )
    subscriptions = models.ManyToManyField(
        Subscription,
        related_name='tg_channels',
        blank=True,
        help_text="List of channel subscriptions.",
    )
    uuid = models.UUIDField()

    def __str__(self):
        return f"TG~{self.name or self.username or self.chat_id!r}"

    @property
    def channel_id(self):
        return self.chat_id or self.username

    def _bot_has_access(self):
        try:
            bot.get_chat(chat_id=self.channel_id)
        except TelegramError:
            raise ValidationError("Bot doesn't have access to this channel.")

    def _bot_id_admin(self):
        admins = bot.get_chat_administrators(chat_id=self.channel_id)
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

    def save(self, update_meta=True, *args, **kwargs):
        if update_meta:
            chat = bot.get_chat(chat_id=self.channel_id)
            self.name = chat.title
            un = chat.username
            if un and not un.startswith('@'):
                un = '@' + un
            self.username = un
            self.chat_id = chat.id
        if not self.uuid:
            self.uuid = uuid.uuid4()
        return super().save(*args, **kwargs)
