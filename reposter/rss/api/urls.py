from django.urls import path

from rss import tasks
from api.views import publish_view_factory, delete_old_posts_view_factory

urlpatterns = [
    path('publish/', publish_view_factory(tasks.fetch_and_publish), name='publish'),
    path('clean/', delete_old_posts_view_factory(tasks.delete_old_posts), name='clean'),
]
