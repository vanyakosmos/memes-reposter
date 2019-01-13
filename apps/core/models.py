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
    REDDIT = 'REDDIT'
    IMGUR = 'IMGUR'
    RSS = 'RSS'
    TYPES = ((REDDIT, 'Reddit'), (IMGUR, 'Imgur'), (RSS, 'RSS'))

    type = models.CharField(max_length=255, choices=TYPES)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.type}.{self.name}"

    def __repr__(self):
        return format_object_repr(self, ['type', 'name'])
