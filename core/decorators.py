from functools import wraps
from telegram import Bot, Update


def admin_access():
    def access(func):
        @wraps(func)
        def wrapped(self, bot: Bot, update: Update, *args, **kwargs):
            user = update.effective_user
            admins = getattr(self, 'admins', None)

            if admins is None:
                self.logger.warning('Specify self.admins (list of users ids) parameter in '
                                    'manager or channel classes in order to restrict access to bot.')
                return func(self, bot, update, *args, **kwargs)

            if user.id not in admins:
                self.logger.info(f"Unauthorized access denied for {user}.")
                return

            return func(self, bot, update, *args, **kwargs)
        return wrapped
    return access
