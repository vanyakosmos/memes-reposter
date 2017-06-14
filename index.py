import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler

from src.database import Database
from src.scheduler import scheduling
from settings import DEBUG, PORT, BOT_TOKEN


logger = logging.getLogger(__name__)


def error(bot, update, err):
    logger.warning(f'Update "{update}" caused error "{err}"')


def boop(bot, update: Update):
    update.message.reply_text('yeah yeah... back to work...')


def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    db = Database('data/database.lol')
    scheduling(updater.job_queue, db)

    dp.add_handler(CommandHandler('boop', boop))
    dp.add_error_handler(error)

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
