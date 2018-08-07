from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView


urlpatterns = [
    path('', RedirectView.as_view(url='admin/')),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),

    path('reddit/', include('apps.reddit.urls')),
    path('imgur/', include('apps.imgur.urls')),
    path('rss/', include('apps.rss.urls')),
]
