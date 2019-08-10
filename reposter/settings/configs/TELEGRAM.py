import easy_env

TELEGRAM_BOT_TOKEN = easy_env.get('TELEGRAM_BOT_TOKEN', raise_error=True)
TELEGRAM_TIMEOUT = 30  # seconds
TELEGRAM_DELETE_OLD_DAYS = easy_env.get_int('TELEGRAM_DELETE_OLD_DAYS', default=7)
