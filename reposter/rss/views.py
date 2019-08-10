from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from . import tasks


@api_view(['POST'])
@permission_classes([IsAdminUser])
def publish_view(request: Request):
    tasks.fetch_and_publish()
    return Response({'status': 'ok'})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def publish_blank_view(request: Request):
    tasks.fetch_and_publish(blank=True)
    return Response({'status': 'ok'})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def delete_old_posts_view(request: Request):
    deleted = tasks.delete_old_posts_db()
    return Response({'deleted': deleted})
