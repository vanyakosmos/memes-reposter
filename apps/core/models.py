from django.db import models
from solo.models import SingletonModel


class SiteConfig(SingletonModel):
    maintenance = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"

    def __str__(self):
        return "Site Configuration"
