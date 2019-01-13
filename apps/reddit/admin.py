from django.contrib import admin
from solo.admin import SingletonModelAdmin

from apps.tgapp.models import TelegramChannel
from .models import Post, RedditConfig, Subreddit


@admin.register(RedditConfig)
class SiteConfigAdmin(SingletonModelAdmin):
    pass


@admin.register(Subreddit)
class SubredditAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'low_score_limit',
        'score_limit',
        'pass_nsfw',
        'show_title',
        'enabled',
        'on_moderation',
        'subs',
    )

    def subs(self, subreddit: Subreddit):
        return ', '.join([str(s) for s in subreddit.subscriptions.all()])


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'status',
        'subreddit_name',
        'type',
        'channel',
    )
    actions = ('make_pending',)
    list_filter = ('status', 'subreddit_name', 'channel_uuid')

    def channel(self, post: Post):
        try:
            channel = TelegramChannel.objects.get(uuid=post.channel_uuid)
            return channel
        except TelegramChannel.DoesNotExist:
            pass

    def make_pending(self, _, qs):
        return qs.update(status=Post.STATUS_PENDING)
