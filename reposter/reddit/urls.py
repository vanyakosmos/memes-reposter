from django.urls import path

from . import views

app_name = 'reddit'

urlpatterns = [
    path('', views.index, name='index'),
    path('publish/', views.publish_view),
    path('blank/', views.blank_publish_view),
    path('posts/', views.PendingPostListView.as_view(), name='list'),
    path('posts/<int:pk>/', views.PostView.as_view(), name='update'),
    path('posts/reject/', views.reject_view, name='reject'),
]
