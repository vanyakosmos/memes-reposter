from django.contrib import admin

from .models import Chat


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'title', 'username', 'type')
    list_filter = ('type',)
    search_fields = ('id', 'username', 'title')
    readonly_fields = ('telegram_id', 'title', 'type')
