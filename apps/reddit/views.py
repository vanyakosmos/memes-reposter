from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import tasks


@api_view(['POST'])
def publish_view(request):
    stats = tasks.fetch_and_publish()
    return Response(stats)


@api_view(['POST'])
def blank_publish_view(request):
    """Save posts into db w/o publishing."""
    stats = tasks.fetch_and_publish(blank=True)
    return Response(stats)
