from django.db import models
from solo.models import SingletonModel

from apps.core.utils import format_object_repr


class SiteConfig(SingletonModel):
    enabled = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"

    def __str__(self):
        return "Site Configuration"

    def __repr__(self):
        return format_object_repr(self, ['enabled'])


class Subscription(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def __repr__(self):
        return format_object_repr(self, ['name'])
