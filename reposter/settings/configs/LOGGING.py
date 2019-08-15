import logging
from os import getenv

logging.addLevelName(logging.DEBUG, '🐛 ')
logging.addLevelName(logging.INFO, '📄️ ')
logging.addLevelName(logging.WARNING, '⚠️ ')
logging.addLevelName(logging.ERROR, '🚨 ')

LOGGING_LEVEL = getenv('LOGGING_LEVEL', 'DEBUG')
LOGGING_LEVEL_ROOT = getenv('LOGGING_LEVEL_ROOT', 'WARNING')

loggers = {
    module: {
        'handlers': ['console'],
        'level': LOGGING_LEVEL,
        'propagate': False,
    }
    for module in ['core', 'imgur', 'reddit', 'rss', 'telegram_app']
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s   %(asctime)s  %(name)10s:%(lineno)-5d  >  %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        **loggers,
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOGGING_LEVEL_ROOT,
        'propagate': False,
    },
}
