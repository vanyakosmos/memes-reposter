import os
import logging


logging.basicConfig(format='%(levelname)-8s %(name)-20s     %(message)s', level=logging.INFO)


DEBUG = False

# heroku
APP_NAME = 'aiven-bot-imgur'
PORT = int(os.environ.get('PORT', '5000'))

# imgur
CLIENT_ID = 'eb6223e9384246d'
CLIENT_SECRET = 'fed4a7e79366b16080aa4433dd45c9cfc414daa3'

# telegram
if DEBUG:
    CHANNEL_ID = '@test_channel_for_vanya'
    BOT_TOKEN = '333977268:AAFEkwrraTlh1WIZMQOjohpw4QCX1dew6kc'
else:
    CHANNEL_ID = '@telemgur'
    BOT_TOKEN = '357603222:AAHtWyUxNRlUWuWekA4aOKG-cNzwfdusdig'

# scheduler
IMGUR_CHECK_INTERVAL = 5 * 60
POSTING_INTERVAL = 0
CLEARING_DB_INTERVAL = 2 * 24 * 60 * 60

# filter
BANNED_TAGS = {'weight loss', 'war', 'army', 'tragedy'}
IMAGES_PER_POST = 10
IMAGES_FOR_LONG_POST = 5
MAX_POST_AGE = 2 * 24 * 60 * 60
MAX_IMAGE_HEIGHT = 1440
MAX_VIDEO_SIZE = 10 * 1024 * 1024
MAX_IMAGE_SIZE = 5 * 1024 * 1024
MIN_DIM_RATIO = 1/4

# publisher
POST_TIMEOUT = 120
