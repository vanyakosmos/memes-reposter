import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import Message
from application.celery import app as celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def delete_old_posts(days=None):
    days = days or settings.TELEGRAM_DELETE_OLD_DAYS
    time = timezone.now() - timedelta(days=days)
    messages = Message.objects.filter(created__lte=time)
    deleted, _ = messages.delete()
    logger.info(f'Deleted {deleted} message(s).')
    return deleted
