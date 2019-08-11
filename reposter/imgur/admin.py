from django.contrib import admin

from .models import Post, ImgurConfig


class SubscriptionInline(admin.TabularInline):
    model = ImgurConfig.subs.through
    extra = 0


@admin.register(ImgurConfig)
class ImgurConfigAdmin(admin.ModelAdmin):
    list_display = (
        'score_limit',
        'allow_albums',
        'exclude_mode',
        'good_tags',
        'bad_tags',
        'active',
    )
    inlines = (SubscriptionInline,)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('imgur_id', 'config', 'title', 'is_album', 'score')
