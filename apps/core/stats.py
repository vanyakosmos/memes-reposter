from enum import Enum, auto
from typing import Optional

from django.conf import settings
from django.utils import timezone
from elasticsearch_dsl import Boolean, Date, Document, Integer, Keyword, Text, connections


class TaskType(Enum):
    PUBLISHING = auto()
    CLEAN_UP = auto()


class AppType(Enum):
    RSS = auto()
    REDDIT = auto()
    IMGUR = auto()


class StatDocument(Document):
    app = Keyword(required=True)
    task = Keyword(required=True)
    note = Text()
    count = Integer(required=True)
    blank = Boolean(required=True)
    created_at = Date(required=True, default_timezone='UTC')

    class Index:
        name = 'stats'


if settings.ELASTIC_URL:
    connections.create_connection(hosts=[settings.ELASTIC_URL], timeout=120)
    StatDocument.init()


def add_stat(app: AppType, task: TaskType = TaskType.PUBLISHING,
             note: Optional[str] = None, count=0, blank=False):
    if not settings.ELASTIC_URL:
        return
    now = timezone.now()
    stat = StatDocument(app=app.name, task=task.name, note=note,
                        count=count, blank=blank, created_at=now)
    stat.save()
