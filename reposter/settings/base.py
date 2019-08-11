import os
from os.path import abspath, dirname, join

import dj_database_url

# noinspection PyUnresolvedReferences
from .configs import *

BASE_DIR = dirname(dirname(abspath(__file__)))
SECRET_KEY = easy_env.get('SECRET_KEY', raise_error=True)
DEBUG = easy_env.get('DEBUG', default=False)
APP_URL = easy_env.get('APP_URL', 'http://0.0.0.0:8000')
ALLOWED_HOSTS = ['*']  # todo: extract host from APP_URL

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    # 3rd parties
    'django_filters',
    'rest_framework',
    'drf_yasg',
    'django_celery_beat',
    # own apps
    'api.apps.ApiConfig',
    'core.apps.CoreConfig',
    'reddit.apps.RedditConfig',
    'telegram_app.apps.TelegramAppConfig',
    'rss.apps.RssConfig',
    'imgur.apps.ImgurConfig',
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

ROOT_URLCONF = 'application.urls'

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

WSGI_APPLICATION = 'application.wsgi.application'

# Database
DATABASE_URL = easy_env.get('DATABASE_URL', 'sqlite:///db.sqlite3')
DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=5 * 60)}

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
STATIC_ROOT = join(BASE_DIR, 'staticfiles')
VIDEOS_ROOT = join(BASE_DIR, 'videos')
os.makedirs(VIDEOS_ROOT, exist_ok=True)
