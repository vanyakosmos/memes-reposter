from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from apps.core.errors import ConfigError
from . import tasks


def poster(posting_task):
    try:
        stats = posting_task()
    except ConfigError as e:
        return Response({
            'details': str(e),
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response(stats)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def publish_view(request):
    poster(tasks.fetch_and_publish)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def blank_publish_view(request):
    """Save posts into db w/o publishing."""
    poster(lambda: tasks.fetch_and_publish(force=True, blank=True))
