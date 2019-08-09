from django.contrib import admin

from .models import Post, Subreddit


@admin.register(Subreddit)
class SubredditAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'score_limit',
        'pass_nsfw',
        'show_title',
        'active',
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'status',
        'comments',
        'subreddit',
        'title',
        'score',
        'nsfw',
    )
    actions = ('make_pending',)
    list_filter = ('status', 'subreddit')

    def make_pending(self, request, qs):
        return qs.update(status=Post.PENDING)
