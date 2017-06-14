import os
import logging


logging.basicConfig(format='%(levelname)-8s %(name)-20s •   %(message)s', level=logging.INFO)


DEBUG = True

PORT = int(os.environ.get('PORT', '5000'))

if DEBUG:
    CHANNEL_ID = '@test_channel_for_vanya'
    BOT_TOKEN = '333977268:AAFEkwrraTlh1WIZMQOjohpw4QCX1dew6kc'
else:
    CHANNEL_ID = '@telemgur'
    BOT_TOKEN = '357603222:AAHtWyUxNRlUWuWekA4aOKG-cNzwfdusdig'


IMGUR_CHECK_INTERVAL = 5 * 60
POSTING_INTERVAL = 3
CLEARING_DB_INTERVAL = 2 * 24 * 60 * 60

POST_TIMEOUT = 30
