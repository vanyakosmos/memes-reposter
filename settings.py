import os
import logging

from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())


def set_up_logging(debug):
    if debug:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    logging.basicConfig(format='%(asctime)s ~ %(levelname)-10s %(name)-25s %(message)s',
                        datefmt='%Y-%m-%d %H:%M',
                        level=logging_level)

    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('JobQueue').setLevel(logging.WARNING)

    logging.addLevelName(logging.DEBUG, '🐛 DEBUG')
    logging.addLevelName(logging.INFO, '📑 INFO')
    logging.addLevelName(logging.WARNING, '🤔 WARNING')
    logging.addLevelName(logging.ERROR, '🚨 ERROR')


DEBUG = os.getenv('DEBUG', 'true').lower() in 'true 1 on ok yes y'.split()

# setup loggers
set_up_logging(debug=DEBUG)
logger = logging.getLogger(__name__)
logger.info(os.getenv('DEBUG'))


# telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')
TEST_CHANNEL_ID = os.getenv('CHANNEL_TEST')


# reddit
REDDIT_USERNAME = os.getenv('REDDIT_NAME')
REDDIT_CHANNEL_ID = TEST_CHANNEL_ID if DEBUG else os.getenv('CHANNEL_REDDIT')


# imgur
IMGUR_CLIENT_ID = os.getenv('IMGUR_CLIENT_ID')
IMGUR_CHANNEL_ID = TEST_CHANNEL_ID if DEBUG else os.getenv('CHANNEL_IMGUR')


# heroku
HEROKU_APP_NAME = os.getenv('APP_NAME')
PORT = int(os.getenv('PORT', '5000'))
HOST = os.getenv('HOST', '0.0.0.0')


# database
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/test')
REDIS_URL = os.getenv("REDIS_URL")
CLEAR_AGE = eval(os.getenv("CLEAR_AGE", '2 * 24 * 60 * 60'))
CLEAR_INTERVAL = eval(os.getenv("CLEAR_INTERVAL", '2 * 24 * 60 * 60'))


# misc
ADMINS = eval(os.getenv('ADMINS', '[]'))
FETCH_LIMIT = int(os.getenv('FETCH_LIMIT', '3')) if DEBUG else 100
