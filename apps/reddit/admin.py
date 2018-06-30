from django.contrib import admin

from .models import Channel, Post, Subreddit


@admin.register(Subreddit)
class SubredditAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'score_limit', 'pass_nsfw', 'show_title', 'active')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'comments', 'subreddit', 'title', 'link')


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'username')
    readonly_fields = ('chat_id',)
