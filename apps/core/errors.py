from rest_framework import status
from rest_framework.exceptions import APIException


class ConfigError(Exception):
    def __init__(self, message: str):
        super(ConfigError, self).__init__(message)


class ServiceUnavailableException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE

