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


class Stat(models.Model):
    TASK_PUBLISHING = 'publishing'
    TASK_CLEAN_UP = 'deleting'
    TASK_CHOICES = (
        (TASK_PUBLISHING, 'Publishing task'),
        (TASK_CLEAN_UP, 'Clean up task'),
    )

    APP_RSS = 'rss'
    APP_REDDIT = 'reddit'
    APP_IMGUR = 'imgur'
    APP_CHOICES = (
        (APP_RSS, 'RSS App'),
        (APP_REDDIT, 'Reddit App'),
        (APP_IMGUR, 'Imgur App'),
    )

    app = models.CharField(max_length=200, choices=APP_CHOICES)
    task = models.CharField(max_length=200, default=TASK_PUBLISHING, choices=TASK_CHOICES)
    note = models.TextField(blank=True, null=True)
    count = models.IntegerField(default=0)
    blank = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.created_at}: {self.app} - {self.count}'

    class Meta:
        verbose_name = "Stats"
        verbose_name_plural = "Stats"
