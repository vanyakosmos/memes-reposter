from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),

    path('reddit/', include('apps.reddit.urls')),
    path('imgur/', include('apps.imgur.urls')),
    path('rss/', include('apps.rss.urls')),
]
