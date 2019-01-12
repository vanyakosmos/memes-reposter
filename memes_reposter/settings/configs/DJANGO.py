import os
from os.path import join
from pathlib import Path

import dj_database_url
import easy_env


BASE_DIR = str(Path(__file__).parents[3])
SECRET_KEY = easy_env.get('SECRET_KEY')
DEBUG = easy_env.get('DEBUG', default=False)
THIS_HOST = easy_env.get('THIS_HOST', 'http://0.0.0.0:8000')
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
    # local apps
    'apps.core.apps.CoreConfig',
    'apps.reddit.apps.RedditConfig',
    'apps.tgapp.apps.TGAppConfig',
    # 'apps.imgur.apps.ImgurConfig',
    # 'apps.rss.apps.RssConfig',
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
DATABASE_URL = easy_env.get('DATABASE_URL', None)
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
VIDEOS_ROOT = join(BASE_DIR, 'videos')
os.makedirs(VIDEOS_ROOT, exist_ok=True)
