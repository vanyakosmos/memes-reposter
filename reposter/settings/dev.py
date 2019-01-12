from .base import *


DEBUG = True
SECRET_KEY = 'secret'
ALLOWED_HOSTS = ['*']

LOGGING['handlers']['console']['level'] = 'DEBUG'
