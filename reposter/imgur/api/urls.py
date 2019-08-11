from django.urls import path

from api.views import publish_view_factory, delete_old_posts_view_factory
from imgur import tasks

urlpatterns = [
    path('publish/', publish_view_factory(tasks.fetch_and_publish), name='publish'),
    path('clean/', delete_old_posts_view_factory(tasks.delete_old_posts), name='clean'),
]
