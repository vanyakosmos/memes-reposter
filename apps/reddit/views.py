from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser

from apps.core.views import poster
from . import tasks


@api_view(['POST'])
@permission_classes([IsAdminUser])
def publish_view(request):
    return poster(tasks.fetch_and_publish)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def blank_publish_view(request):
    """Save posts into db w/o publishing."""
    return poster(lambda: tasks.fetch_and_publish(force=True, blank=True))
