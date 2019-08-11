from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='admin/')),
    path('admin/', admin.site.urls),
    path('admin/jet/', include('jet.urls', 'jet')),
    path('api/drf-auth/', include('rest_framework.urls')),
    path('api/', include('api.urls')),
    path('reddit/', include('reddit.urls')),
    re_path(r'^videos/(?P<path>.*)$', views.stream_video),
]
