import easy_env

REDDIT_POSTS_LIMIT = easy_env.get_int('REDDIT_POSTS_LIMIT', default=20)
REDDIT_DELETE_OLD_DAYS = easy_env.get_int('REDDIT_DELETE_OLD_DAYS', default=3)
