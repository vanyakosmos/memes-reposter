from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from . import tasks


@api_view(['POST'])
@permission_classes([IsAdminUser])
def publish_view(request):
    tasks.fetch_and_publish()
    return Response({'status': 'ok'})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def blank_publish_view(request):
    """Save posts into db w/o publishing."""
    tasks.fetch_and_publish(blank=True)
    return Response({'status': 'ok'})
