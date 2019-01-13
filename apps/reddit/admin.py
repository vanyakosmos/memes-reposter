from django.contrib import admin
from solo.admin import SingletonModelAdmin

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
        'file_path',
        'status',
        'comments',
        'subreddit_name',
        'title',
        'source_url',
        'type',
        'score',
        'nsfw',
    )
    actions = ('make_pending',)
    list_filter = ('status', 'subreddit_name')

    def make_pending(self, _, qs):
        return qs.update(status=Post.STATUS_PENDING)
