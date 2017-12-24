import os

from dotenv import find_dotenv, load_dotenv

from settings.logging import set_up_logging


load_dotenv(find_dotenv())


DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'


# setup loggers
set_up_logging(debug=DEBUG)


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
