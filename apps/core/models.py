from django.db import models
from solo.models import SingletonModel

from .errors import ConfigError


class SiteConfig(SingletonModel):
    maintenance = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"

    def __str__(self):
        return "Site Configuration"

    def check_maintenance(self, force=False):
        if self.maintenance and not force:
            raise ConfigError('Site in maintenance mode, skipping publishing.')
