from telegram_autoposter.manager import Manager

from reddit import RedditChannel
from settings import BOT_TOKEN, DEBUG, HEROKU_PORT, HOST, HEROKU_APP_NAME


if __name__ == '__main__':
    manager = Manager(token=BOT_TOKEN)
    manager.config(env=('dev' if DEBUG else 'prod'),
                   port=HEROKU_PORT,
                   host=HOST,
                   webhook_url=f'https://{HEROKU_APP_NAME}.herokuapp.com/{BOT_TOKEN}')
    manager.register(RedditChannel)
    manager.start()
