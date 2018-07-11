from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('reddit/', include('apps.reddit.urls')),
    path('imgur/', include('apps.imgur.urls')),
    path('rss/', include('apps.rss.urls')),
]
