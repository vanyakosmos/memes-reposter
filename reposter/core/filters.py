import logging
from functools import wraps


def log_size(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        posts = args[0]
        init_len = len(posts)
        result = func(*args, **kwargs)
        logger = logging.getLogger(func.__module__)
        logger.info('Filter %s: %d > %d', func.__name__, init_len, len(result))
        return result
    return wrapper
