from django.contrib import admin

from .models import Post, ImgurConfig


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


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('imgur_id', 'config', 'title')
