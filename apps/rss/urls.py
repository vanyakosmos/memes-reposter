from django.urls import path

from . import views

app_name = 'rss'

urlpatterns = [
    path('', views.index_view, name='root'),
    path('publish/', views.publish_view, name='publish'),
    path('refresh/', views.refresh_view, name='refresh'),
    path('clean/', views.delete_old_posts_view, name='clean'),
    path('channels/', views.channels_view, name='channels'),
]
