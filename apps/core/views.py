from rest_framework import status
from rest_framework.response import Response

from .errors import ConfigError


def poster(posting_task):
    try:
        posting_task()
    except ConfigError as e:
        return Response({
            'details': str(e),
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response()
