import os
import logging


from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'


# setup loggers
if DEBUG:
    logging_level = logging.DEBUG
else:
    logging_level = logging.INFO

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
HEROKU_APP_NAME = os.getenv('APP_NAME')
HEROKU_PORT = int(os.getenv('PORT', '5000'))


# database
REDIS_URL = os.getenv("REDIS_URL")


# imgur
IMGUR_CLIENT_ID = os.getenv('IMGUR_CLIENT_ID')


# telegram
TELEMGUR_CHANNEL_ID = os.getenv('CHANNEL_TELEMGUR')
SUBREDDIT_CHANNEL_ID = os.getenv('CHANNEL_SUBREDDIT')
if DEBUG:
    TELEMGUR_CHANNEL_ID = os.getenv('CHANNEL_TEST')
    SUBREDDIT_CHANNEL_ID = os.getenv('CHANNEL_TEST')
BOT_TOKEN = os.getenv('BOT_TOKEN')


# scheduler
IMGUR_CHECK_INTERVAL = 10 * 60
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


# setup
LIST_OF_ADMINS = [int(os.getenv('ADMIN')), ]
