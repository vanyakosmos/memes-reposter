from django.urls import path

from . import views

app_name = 'rss'

urlpatterns = [
    path('publish/', views.publish_view, name='publish'),
    path('blank/', views.publish_blank_view, name='blank'),
    path('clean/', views.delete_old_posts_view, name='clean'),
]
