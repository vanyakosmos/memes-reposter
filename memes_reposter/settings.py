import logging
import multiprocessing
from os.path import abspath, dirname, join

import dj_database_url
import easy_env
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())

BASE_DIR = dirname(dirname(abspath(__file__)))
SECRET_KEY = easy_env.get('SECRET_KEY', raise_error=True)
DEBUG = easy_env.get('DEBUG', default=False)
THIS_HOST = easy_env.get('THIS_HOST', '0.0.0.0:8000')
ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',  # whitenoise support in dev
    'django.contrib.staticfiles',
    # 3rd parties
    'solo.apps.SoloAppConfig',
    'rest_framework',
    'django_celery_beat',
    # own apps
    'apps.core.apps.CoreConfig',
    'apps.reddit.apps.RedditConfig',
    'apps.imgur.apps.ImgurConfig',
    'apps.rss.apps.RssConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'memes_reposter.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'memes_reposter.wsgi.application'

# Database
DATABASE_URL = easy_env.get('DATABASE_URL', 'sqlite:///db.sqlite3')
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL)
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = join(BASE_DIR, 'static')

# logging
logging.addLevelName(logging.DEBUG, '🐛 ')
logging.addLevelName(logging.INFO, '📄️ ')
logging.addLevelName(logging.WARNING, '⚠️ ')
logging.addLevelName(logging.ERROR, '🚨 ')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s   %(asctime)s  %(name)10s:%(lineno)-5d  ⏩  %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        '': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# rest
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10
}

# telegram
TELEGRAM_BOT_TOKEN = easy_env.get('TELEGRAM_BOT_TOKEN', raise_error=True)
TELEGRAM_TIMEOUT = 30  # seconds

# celery
REDIS_URL = easy_env.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_BROKER_URL = REDIS_URL
CELERY_TASK_SERIALIZER = 'json'
CELERY_WORKER_CONCURRENCY = easy_env.get_int('CELERY_WORKER_CONCURRENCY',
                                             default=multiprocessing.cpu_count())
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# core
ELASTIC_URL = easy_env.get_str('ELASTIC_URL')
ADMINS = easy_env.get_list('ADMINS', [], item_factory=int)

# reddit
REDDIT_FETCH_SIZE = easy_env.get_int('REDDIT_FETCH_SIZE', default=100)

# imgur
IMGUR_CLIENT_ID = easy_env.get('IMGUR_CLIENT_ID')
IMGUR_FETCH_LIMIT = easy_env.get_int('IMGUR_FETCH_LIMIT', default=100)
IMGUR_DELETE_ON_FAIL = easy_env.get_bool('IMGUR_DELETE_ON_FAIL', default=True)

# rss
RSS_CLEAN_KEEP = easy_env.get_int('RSS_CLEAN_KEEP', default=30)
