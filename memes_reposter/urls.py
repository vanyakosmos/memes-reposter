from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from . import views


api_patterns = [
    path('drf_auth/', include('rest_framework.urls')),
    path('reddit/', include('apps.reddit.urls')),
    # path('imgur/', include('apps.imgur.urls')),
    # path('rss/', include('apps.rss.urls')),
]

urlpatterns = [
    path('', RedirectView.as_view(url='admin/')),
    path('admin/', admin.site.urls),
    path('api/', include(api_patterns)),
    re_path(r'^videos/(?P<path>.*)$', views.stream_video, name='video'),
]
