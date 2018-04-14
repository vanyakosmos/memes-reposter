import logging
from functools import wraps

from telegram import Bot, Update


def admin_access(admins_list=None):
    def access(func):
        logger = logging.getLogger(__name__)

        @wraps(func)
        def wrapped(self, bot: Bot, update: Update, *args, **kwargs):
            user = update.effective_user
            admins = None
            if admins_list is None:
                admins = getattr(self, 'admins', None)

            if admins is None:
                logger.warning('Specify self.admins (list of users ids) parameter in '
                               'manager or channel classes in order to restrict access to bot.')
                return func(self, bot, update, *args, **kwargs)

            if user.id not in admins:
                logger.info(f"Unauthorized access denied for {user}.")
                return

            return func(self, bot, update, *args, **kwargs)

        return wrapped

    return access


def log(func):
    logger = logging.getLogger(func.__module__)

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        logger.debug('Called ::' + func.__name__)
        return func(self, *args, **kwargs)

    return wrapper


def mega_log(print_res=False, print_end=False):
    def decorator(func):
        logger = logging.getLogger(func.__module__)

        @wraps(func)
        def wrapped(self, *args, **kwargs):
            logger.debug('Entering: %s', func.__name__)
            result = func(self, *args, **kwargs)
            if print_res:
                logger.debug(result)
            if print_end:
                logger.debug('Exiting: %s', func.__name__)
            return result

        return wrapped

    return decorator
