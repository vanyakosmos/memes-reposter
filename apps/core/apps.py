from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'apps.core'

    def ready(self):
        from .models import Subscription

        Subscription.objects.get_or_create(name='reddit main')
        Subscription.objects.get_or_create(name='imgur main')
        Subscription.objects.get_or_create(name='rss main')
