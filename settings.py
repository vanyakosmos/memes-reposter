import os
import logging

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
"""
With ``dotenv`` you can create `.env` file in the same directory and setup your own environmental variables.
Example of `.env` file:

    DEBUG=true
    
    # telegram
    BOT_TOKEN=12345:12345
    
    # imgur
    IMGUR_CLIENT_ID=12345
    
    # heroku
    APP_NAME=bla-bla
    PORT=5000
    REDIS_URL=redis://127.0.0.1:6379/0
    
    # setup
    ADMIN=12345
"""


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
REDDIT_NAME = os.getenv('REDDIT_NAME')


# telegram
TELEMGUR_CHANNEL_ID = os.getenv('CHANNEL_TELEMGUR')
SUBREDDIT_CHANNEL_ID = os.getenv('CHANNEL_SUBREDDIT')
if DEBUG:
    TELEMGUR_CHANNEL_ID = os.getenv('CHANNEL_TEST')
    SUBREDDIT_CHANNEL_ID = os.getenv('CHANNEL_TEST')
BOT_TOKEN = os.getenv('BOT_TOKEN')


# scheduler
CHECK_INTERVAL = eval(os.getenv('CHECK_INTERVAL'))
POSTING_INTERVAL = eval(os.getenv('POSTING_INTERVAL'))
CLEARING_DB_INTERVAL = eval(os.getenv('CLEARING_DB_INTERVAL'))


# filter
BANNED_TAGS = eval(os.getenv('BANNED_TAGS'))
IMAGES_PER_POST = int(os.getenv('IMAGES_PER_POST'))
IMAGES_FOR_LONG_POST = int(os.getenv('IMAGES_FOR_LONG_POST'))
MAX_VIDEO_SIZE = eval(os.getenv('MAX_VIDEO_SIZE'))
MAX_IMAGE_SIZE = eval(os.getenv('MAX_IMAGE_SIZE'))
MIN_DIM_RATIO = eval(os.getenv('MIN_DIM_RATIO'))


# publisher
POST_TIMEOUT = int(os.getenv('POST_TIMEOUT'))


# setup
LIST_OF_ADMINS = [int(os.getenv('ADMIN')), ]
