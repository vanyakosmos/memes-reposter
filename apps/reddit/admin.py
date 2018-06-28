from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import Post, RedditConfig, Subreddit


@admin.register(Subreddit)
class SubredditAdmin(admin.ModelAdmin):
    pass


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass


@admin.register(RedditConfig)
class RedditConfigAdmin(SingletonModelAdmin):
    pass
