import os
import logging


logging.basicConfig(format='%(levelname)-8s %(name)-20s     %(message)s', level=logging.INFO)


DEBUG = False

PORT = int(os.environ.get('PORT', '5000'))

# Imgur
CLIENT_ID = 'eb6223e9384246d'
CLIENT_SECRET = 'fed4a7e79366b16080aa4433dd45c9cfc414daa3'

# Telegram
if DEBUG:
    CHANNEL_ID = '@test_channel_for_vanya'
    BOT_TOKEN = '333977268:AAFEkwrraTlh1WIZMQOjohpw4QCX1dew6kc'
else:
    CHANNEL_ID = '@telemgur'
    BOT_TOKEN = '357603222:AAHtWyUxNRlUWuWekA4aOKG-cNzwfdusdig'

# scheduler
IMGUR_CHECK_INTERVAL = 5 * 60
POSTING_INTERVAL = 15
CLEARING_DB_INTERVAL = 2 * 24 * 60 * 60

# filter
BANNED_TAGS = {'weight loss', }
IMAGES_PER_POST = 9
IMAGES_FOR_LONG_POST = 3
MAX_POST_AGE = 8 * 60 * 60

# publisher
POST_TIMEOUT = 30
