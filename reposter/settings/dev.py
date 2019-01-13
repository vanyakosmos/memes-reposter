from .base import *


DEBUG = True
SECRET_KEY = 'secret'
ALLOWED_HOSTS = ['*']


#
# logging adjustments
#

def logger_setup(level: str):
    return {
        'handlers': ['console'],
        'level': level.upper(),
        'propagate': False,
    }


LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['apps.tgapp.publishers.reddit'] = logger_setup('info')
LOGGING['loggers']['apps.reddit.utils'] = logger_setup('info')
