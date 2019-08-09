from django.contrib import admin

from .models import Chat, Message


class SubscriptionInline(admin.TabularInline):
    model = Chat.subs.through
    extra = 0


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'title', 'username', 'type')
    list_filter = ('type',)
    search_fields = ('id', 'username', 'title')
    readonly_fields = ('telegram_id', 'title', 'type')

    inlines = [SubscriptionInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_id', 'message_id')

    def chat_id(self, msg: Message):
        return msg.chat.telegram_id
