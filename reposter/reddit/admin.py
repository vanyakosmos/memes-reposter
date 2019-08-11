from django.contrib import admin

from .models import Post, Subreddit


class SubscriptionInline(admin.TabularInline):
    model = Subreddit.subs.through
    extra = 0


@admin.register(Subreddit)
class SubredditAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'score_limit',
        'pass_nsfw',
        'show_title',
        'active',
    )
    inlines = (SubscriptionInline,)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'status',
        'subreddit_name',
        'title',
        'score',
        'nsfw',
    )
    actions = ('make_pending',)
    list_filter = ('status', 'subreddit')

    def make_pending(self, request, qs):
        return qs.update(status=Post.PENDING)
