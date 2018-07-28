from django.contrib import admin

from .models import Channel, Post, Subreddit


@admin.register(Subreddit)
class SubredditAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'low_score_limit', 'score_limit', 'pass_nsfw',
                    'show_title', 'active', 'on_moderation')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status', 'comments', 'subreddit', 'title',
                    'media_link', 'media_type', 'score', 'nsfw')
    readonly_fields = ('subreddit', 'title', 'link', 'reddit_id', 'created', 'text',
                       'media_link', 'media_type', 'score', 'nsfw')


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'username')
    readonly_fields = ('chat_id',)
