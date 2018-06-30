from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import tasks


@api_view(['POST'])
def publish_view(request):
    stats = tasks.fetch_and_publish()
    if stats:
        return Response(stats)
    else:
        return Response({
            'details': 'Site in maintenance mode. Try again later.'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['POST'])
def blank_publish_view(request):
    """Save posts into db w/o publishing."""
    stats = tasks.fetch_and_publish(blank=True, force=True)
    return Response(stats)
