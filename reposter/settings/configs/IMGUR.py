import easy_env

IMGUR_CLIENT_ID = easy_env.get('IMGUR_CLIENT_ID')
IMGUR_FETCH_LIMIT = easy_env.get_int('IMGUR_FETCH_LIMIT', default=100)
IMGUR_DELETE_ON_FAIL = easy_env.get_bool('IMGUR_DELETE_ON_FAIL', default=True)
IMGUR_DELETE_OLD_DAYS = easy_env.get_int('IMGUR_DELETE_OLD_DAYS', default=3)
