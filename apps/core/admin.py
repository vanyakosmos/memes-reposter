from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import SiteConfig


@admin.register(SiteConfig)
class SiteConfigAdmin(SingletonModelAdmin):
    pass
