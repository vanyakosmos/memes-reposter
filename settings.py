import os
import logging


DEBUG = False

if DEBUG:
    logging_level = logging.DEBUG
else:
    logging_level = logging.INFO


# setup loggers
logging.basicConfig(format='%(asctime)s ~ %(levelname)-10s %(name)-25s %(message)s',
                    datefmt='%Y-%m-%d %H:%M',
                    level=logging_level)
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('JobQueue').setLevel(logging.WARNING)
logging.addLevelName(logging.DEBUG,     '🐛 DEBUG')
logging.addLevelName(logging.INFO,      '📑 INFO')
logging.addLevelName(logging.WARNING,   '🤔 WARNING')
logging.addLevelName(logging.ERROR,     '🚨 ERROR')


# heroku
APP_NAME = str(os.environ.get('APP_NAME'))
PORT = int(os.environ.get('PORT', '5000'))
REDIS_URL = os.environ.get("REDIS_URL")


# imgur
CLIENT_ID = 'eb6223e9384246d'
CLIENT_SECRET = 'fed4a7e79366b16080aa4433dd45c9cfc414daa3'


# telegram
if DEBUG:
    TELEMGUR_CHANNEL_ID = '@test_channel_for_vanya'
    SUBREDDIT_CHANNEL_ID = '@test_channel_for_vanya'
    BOT_TOKEN = '333977268:AAFEkwrraTlh1WIZMQOjohpw4QCX1dew6kc'
else:
    TELEMGUR_CHANNEL_ID = '@telemgur'
    SUBREDDIT_CHANNEL_ID = '@pop_reddit'
    BOT_TOKEN = str(os.environ.get('BOT_TOKEN'))


# scheduler
IMGUR_CHECK_INTERVAL = 5 * 60
POSTING_INTERVAL = 0
CLEARING_DB_INTERVAL = 2 * 24 * 60 * 60


# filter
BANNED_TAGS = {'weight loss', 'war', 'army', 'tragedy'}
IMAGES_PER_POST = 10
IMAGES_FOR_LONG_POST = 5
MAX_POST_AGE = 2 * 24 * 60 * 60
MAX_VIDEO_SIZE = 10 * 1024 * 1024
MAX_IMAGE_SIZE = 3 * 1024 * 1024
MIN_DIM_RATIO = 1/4


# publisher
POST_TIMEOUT = 60
