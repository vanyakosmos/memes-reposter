from typing import Callable

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from .serializers import PublishRequest, CleanUpRequest


def publish_view_factory(fetch_and_publish: Callable):
    @swagger_auto_schema(
        method='post',
        operation_id=f'publish posts',
        request_body=PublishRequest,
        responses={status.HTTP_201_CREATED: 'empty'}
    )
    @api_view(['POST'])
    @permission_classes([IsAdminUser])
    def view(request: Request):
        blank = request.data.get('blank') == '1'
        fetch_and_publish(blank)
        return Response(status=status.HTTP_201_CREATED)

    return view


def delete_old_posts_view_factory(delete_old_posts: Callable):
    @swagger_auto_schema(
        method='post',
        operation_id=f'delete old posts',
        request_body=CleanUpRequest,
        responses={status.HTTP_201_CREATED: 'empty'}
    )
    @api_view(['POST'])
    @permission_classes([IsAdminUser])
    def view(request: Request):
        s = CleanUpRequest(data=request.data)
        s.is_valid(raise_exception=True)
        days = s.validated_data.get('days')
        if days is not None:
            try:
                days = int(days)
            except ValueError:
                raise ValidationError("Invalid 'days' param.")
        delete_old_posts(days)
        return Response(status=status.HTTP_201_CREATED)

    return view
