import logging
import os

import telegram
from telegram.ext import Updater

from src.data_fetcher import get_data_from_imgur
from src.filter import filter_posts
from src.database import Database
from src.publisher import publish_posts_guarded


logging.basicConfig(format='%(levelname)10s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


DEBUG = False
PORT = int(os.environ.get('PORT', '5000'))

if DEBUG:
    CHANNEL_ID = '@test_channel_for_vanya'
    BOT_TOKEN = '333977268:AAFEkwrraTlh1WIZMQOjohpw4QCX1dew6kc'
else:
    CHANNEL_ID = '@telemgur'
    BOT_TOKEN = '357603222:AAHtWyUxNRlUWuWekA4aOKG-cNzwfdusdig'


def post_images(bot, job):
    db = job.context
    """Function to send the alarm message"""
    data = get_data_from_imgur()
    if data["success"]:
        logging.info('Got data form Imgur')
        posts = filter_posts(data['data'], db)
    else:
        logging.warning('Couldn\'t fetch data from Imgur')
        return

    publish_posts_guarded(bot, CHANNEL_ID, posts, db)


def clear_db(bot: telegram.Bot, job):
    logger.info('Perform database clearing...')
    db, period = job.context
    deleted_count = db.clear(period)
    logger.info(f'Cleared: {deleted_count} post(s)')


def schedule(updater, db):
    imgur_check_interval = 10 * 60
    clear_db_interval = 2 * 24 * 60 * 60

    updater.job_queue.run_repeating(post_images, first=0, interval=imgur_check_interval, context=db)
    updater.job_queue.run_repeating(clear_db, interval=clear_db_interval, context=(db, clear_db_interval))
    logger.info('Loops scheduled')


def main():
    updater = Updater(BOT_TOKEN)

    db = Database('data/database.lol')
    schedule(updater, db)

    if DEBUG:
        updater.start_polling()
    else:
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=BOT_TOKEN)
        updater.bot.set_webhook("https://aiven-bot-hater.herokuapp.com/" + BOT_TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
