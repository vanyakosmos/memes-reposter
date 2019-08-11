from django.urls import path, re_path, include
from django.views.generic import RedirectView
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, *args, **kwargs):
        schema = super().get_schema(*args, **kwargs)
        schema.basePath = '/api'  # API prefix
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title="Reposter API",
        default_version='v1',
        description='Try out the API with the <a href="/api/client/">Swagger API Client</a>',
        license=openapi.License(name="MIT"),
    ),
    urlconf='api.urls',
    permission_classes=(IsAdminUser,),
    authentication_classes=(SessionAuthentication,),
    generator_class=CustomOpenAPISchemaGenerator,
)

auth_urls = [
    path(r'obtain/', obtain_jwt_token),
    path(r'refresh/', refresh_jwt_token),
    path(r'verify/', verify_jwt_token),
]

urlpatterns = [
    # API Documentation
    re_path(
        r'^schema(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=None),
        name='api-schema',
    ),
    path('', RedirectView.as_view(url='docs/')),
    path('docs/', schema_view.with_ui('redoc', cache_timeout=None), name='api-docs'),
    path('client/', schema_view.with_ui('swagger', cache_timeout=None), name='api-client'),

    # Auth
    path('auth/', include(auth_urls)),
    # API endpoints
    path('reddit/', include('reddit.api.urls')),
    path('imgur/', include('imgur.api.urls')),
    path('rss/', include('rss.api.urls')),
]
