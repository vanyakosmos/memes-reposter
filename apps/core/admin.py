from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import SiteConfig, Subscription


@admin.register(SiteConfig)
class SiteConfigAdmin(SingletonModelAdmin):
    pass


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name',)
