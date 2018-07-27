from django.urls import path

from apps.reddit import views


app_name = 'reddit'

urlpatterns = [
    path('publish/', views.publish_view),
    path('blank/', views.blank_publish_view),

    path('', views.index, name='index'),
    path('posts/', views.PendingPostListView.as_view(), name='list'),
    path('posts/<int:pk>/', views.PostView.as_view(), name='update'),
]
