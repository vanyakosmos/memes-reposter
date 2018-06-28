from django.urls import path

from apps.reddit import views


urlpatterns = [
    path('publish/', views.publish_view)
]
