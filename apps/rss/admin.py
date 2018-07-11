from datetime import timedelta

from django.contrib import admin
from django.db.models import Case, Value, When
from django.utils import timezone

from .models import Channel, Post, RssFeed


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'title', 'username', 'publish_picture', 'linked_title', 'short_link')
    change_list_template = "rss/actions.html"


@admin.register(RssFeed)
class RssFeedAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'channel', 'link', 'active')
    actions = ('activate', 'deactivate', 'toggle_active')

    def activate(self, request, queryset):
        queryset.update(active=True)

    def deactivate(self, request, queryset):
        queryset.update(active=False)

    def toggle_active(self, request, queryset):
        queryset.update(active=Case(When(active=True, then=Value(False)), default=Value(True)))


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'feed', 'link', 'created', 'older_then_five_days')
    ordering = ('-created',)

    def older_then_five_days(self, post: Post):
        five_days_before = timezone.now() - timedelta(days=5)
        return post.created < five_days_before

    older_then_five_days.boolean = True
