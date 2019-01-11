import easy_env


TELEGRAM_BOT_TOKEN = easy_env.get('TELEGRAM_BOT_TOKEN', raise_error=True)
TELEGRAM_TIMEOUT = 30  # seconds
TG_ADMINS = easy_env.get_list('ADMINS', [], item_factory=int)
