import logging

from telegram import Bot
from telegram import Update

from autoposter import Manager
from settings import DEBUG, PORT, BOT_TOKEN, APP_NAME
from src.setups import RedditSetup, ImgurSetup


def error(_: Bot, update: Update, err: Exception):
    logging.warning(f'Update "{update}" caused error "{err}"')


def main():
    manager = Manager(BOT_TOKEN)

    imgur_setup = ImgurSetup('telemgur')
    reddit_setup = RedditSetup('pop_reddit')
    manager.register(
        imgur_setup,
        reddit_setup,
    )

    if DEBUG:
        manager.start_polling()
    else:
        manager.start_webhook(listen="0.0.0.0", port=PORT, url_path=BOT_TOKEN,
                              webhook_url=f"https://{APP_NAME}.herokuapp.com/{BOT_TOKEN}")


if __name__ == '__main__':
    main()
