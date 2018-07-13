import logging
from datetime import timedelta

from celery.schedules import crontab
from django.utils import timezone

from memes_reposter.celery import app as celery_app
from .models import Stat


logger = logging.getLogger(__name__)


@celery_app.task
def delete_old_stats():
    time = timezone.now() - timedelta(days=3)
    stats = Stat.objects.filter(created_at__lte=time)
    deleted, _ = stats.delete()
    logger.info(f'Deleted {deleted} stat(s).')
    return deleted


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **_):
    logger.info('SCHEDULING CORE')
    clean_crontab = crontab(hour='*/12', minute='55')
    sender.add_periodic_task(clean_crontab, delete_old_stats.s(), name='core.clean_up')
