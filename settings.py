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


# telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')
IMGUR_CHANNEL_ID = os.getenv('CHANNEL_TELEMGUR')
REDDIT_CHANNEL_ID = os.getenv('CHANNEL_SUBREDDIT')
if DEBUG:
    IMGUR_CHANNEL_ID = os.getenv('CHANNEL_TEST')
    REDDIT_CHANNEL_ID = os.getenv('CHANNEL_TEST')


# heroku
HEROKU_APP_NAME = os.getenv('APP_NAME')
HEROKU_PORT = int(os.getenv('PORT', '5000'))
HOST = os.getenv('HOST', '0.0.0.0')


# database
REDIS_URL = os.getenv("REDIS_URL")


# misc
LIST_OF_ADMINS = [int(os.getenv('ADMIN')), ]
FETCH_LIMIT = int(os.getenv('FETCH_LIMIT')) if DEBUG else 100


reddit_settings = {
    'channel_id': REDDIT_CHANNEL_ID,
    'username': os.getenv('REDDIT_NAME'),
    'post_interval': eval(os.getenv('REDDIT_POST_INTERVAL', '20 * 60')),
    'db_clear_age': eval(os.getenv('REDDIT_DB_CLEAR_AGE', '1 * 24 * 60 * 60')),
    'db_clear_interval': eval(os.getenv('REDDIT_DB_CLEAR_INTERVAL', '1 * 24 * 60 * 60')),
}

imgur_settings = {
    'channel_id': IMGUR_CHANNEL_ID,
    'client_id': os.getenv('IMGUR_CLIENT_ID'),
    'post_interval': eval(os.getenv('IMGUR_POST_INTERVAL', '20 * 60')),
    'db_clear_age': eval(os.getenv('IMGUR_DB_CLEAR_AGE', '1 * 24 * 60 * 60')),
    'db_clear_interval': eval(os.getenv('IMGUR_DB_CLEAR_INTERVAL', '1 * 24 * 60 * 60')),
    'max_video_size': eval(os.getenv('MAX_VIDEO_SIZE')),
    'max_image_size': eval(os.getenv('MAX_IMAGE_SIZE')),
    'min_dim_ratio': eval(os.getenv('MIN_DIM_RATIO')),
}

# move in-store settings
BANNED_TAGS = eval(os.getenv('BANNED_TAGS'))
IMAGES_PER_POST = int(os.getenv('IMAGES_PER_POST'))
IMAGES_FOR_LONG_POST = int(os.getenv('IMAGES_FOR_LONG_POST'))
