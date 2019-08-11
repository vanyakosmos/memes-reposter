import logging

from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Schedule publishing and clean up tasks.'

    def schedule_reddit(self):
        self.stdout.write(self.style.SUCCESS('SCHEDULING REDDIT TASKS'))
        # publish
        cron, _ = CrontabSchedule.objects.get_or_create(minute='0,30')
        task = PeriodicTask.objects.get_or_create(
            crontab=cron,
            name='reddit.publish',
            task='reddit.tasks.fetch_and_publish',
        )
        self.stdout.write(str(task))
        # clean up
        cron, _ = CrontabSchedule.objects.get_or_create(hour='*/12', minute='55')
        task = PeriodicTask.objects.get_or_create(
            crontab=cron,
            name='reddit.clean_up',
            task='reddit.tasks.delete_old_posts',
        )
        self.stdout.write(str(task))

    def schedule_imgur(self):
        self.stdout.write(self.style.SUCCESS('SCHEDULING IMGUR TASKS'))
        # publish
        cron, _ = CrontabSchedule.objects.get_or_create(minute='5,35')
        task = PeriodicTask.objects.get_or_create(
            crontab=cron,
            name='imgur.publish',
            task='imgur.tasks.fetch_and_publish',
        )
        self.stdout.write(str(task))
        # clean up
        cron, _ = CrontabSchedule.objects.get_or_create(hour='*/12', minute='55')
        task = PeriodicTask.objects.get_or_create(
            crontab=cron,
            name='imgur.clean_up',
            task='imgur.tasks.delete_old_posts',
        )
        self.stdout.write(str(task))

    def schedule_rss(self):
        self.stdout.write(self.style.SUCCESS('SCHEDULING RSS TASKS'))
        # publish
        cron, _ = CrontabSchedule.objects.get_or_create(minute='10,40')
        task = PeriodicTask.objects.get_or_create(
            crontab=cron,
            name='rss.publish',
            task='rss.tasks.fetch_and_publish',
        )
        self.stdout.write(str(task))
        # clean up
        cron, _ = CrontabSchedule.objects.get_or_create(hour='*/12', minute='55')
        task = PeriodicTask.objects.get_or_create(
            crontab=cron,
            name='rss.clean_up',
            task='rss.tasks.delete_old_posts',
        )
        self.stdout.write(str(task))

    def handle(self, *args, **options):
        self.schedule_reddit()
        self.schedule_imgur()
        self.schedule_rss()
