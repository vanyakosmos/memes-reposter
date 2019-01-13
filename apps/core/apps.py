from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'apps.core'

    def ready(self):
        from .models import Subscription

        Subscription.objects.get_or_create(type=Subscription.REDDIT, name='main')
        Subscription.objects.get_or_create(type=Subscription.IMGUR, name='main')
        Subscription.objects.get_or_create(type=Subscription.RSS, name='main')
