from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import tasks


@api_view(['POST'])
def publish_view(request):
    stats = tasks.fetch_and_publish()
    return Response(stats)
