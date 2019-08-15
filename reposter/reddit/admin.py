from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Post, Subreddit


class SubscriptionInline(admin.TabularInline):
    model = Subreddit.subs.through
    extra = 0


@admin.register(Subreddit)
class SubredditAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'score_limit',
        'score_limit_repost',
        'pass_nsfw',
        'show_title',
        'active',
        'posts',
    )
    inlines = (SubscriptionInline,)

    def posts(self, sub: Subreddit):
        url = reverse('admin:reddit_post_changelist')
        url += f'?subreddit__id__exact={sub.id}'
        return mark_safe(f'<a href="{url}">posts</a>')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'post',
        'title',
        'status',
        'subreddit_name',
        'score',
        'nsfw',
        'type',
    )
    actions = ('make_pending',)
    list_filter = ('status', 'subreddit')

    def post(self, post: Post):
        return render_to_string('reddit/post.html', {'post': post})

    def make_pending(self, request, qs):
        return qs.update(status=Post.PENDING)
