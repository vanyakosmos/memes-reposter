import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memes_reposter.settings')

app = Celery('memes_reposter')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
