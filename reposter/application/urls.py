from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='admin/')),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('reddit/', include('reddit.urls')),
    # path('imgur/', include('imgur.urls')),
    # path('rss/', include('rss.urls')),
    re_path(r'^videos/(?P<path>.*)$', views.stream_video),
]
