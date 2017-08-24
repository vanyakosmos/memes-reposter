from core.manager import Manager

from reddit import RedditChannel
from imgur import ImgurChannel
from settings import BOT_TOKEN, DEBUG, PORT, HOST, HEROKU_APP_NAME, ADMINS

if __name__ == '__main__':
    manager = Manager(token=BOT_TOKEN, admins=ADMINS)

    manager.register(RedditChannel())
    manager.register(ImgurChannel())

    if DEBUG:
        manager.start_polling()
    else:
        manager.start_webhook(listen=HOST, port=PORT, url_path=BOT_TOKEN,
                              webhook_url=f'https://{HEROKU_APP_NAME}.herokuapp.com/{BOT_TOKEN}')
