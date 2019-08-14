from django.urls import path

from api.views import publish_view_factory, delete_old_posts_view_factory
from reddit.api import views
from reddit import tasks

app_name = 'reddit'
urlpatterns = [
    path('publish/', publish_view_factory(tasks.fetch_and_publish), name='publish'),
    path('clean/', delete_old_posts_view_factory(tasks.delete_old_posts), name='clean'),
    path('posts/', views.PostsListView.as_view(), name='list'),
    path('posts/<int:pk>/', views.PostView.as_view(), name='update'),
    path('posts/reject/', views.reject_view, name='reject'),
    path('posts/subreddits/', views.pending_subreddits_view, name='pending_subs'),
]
