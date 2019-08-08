from django.contrib import admin

from .models import Post, ImgurConfig
from solo.admin import SingletonModelAdmin


@admin.register(ImgurConfig)
class ImgurConfigAdmin(SingletonModelAdmin):
    readonly_fields = ('chat_id',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass
