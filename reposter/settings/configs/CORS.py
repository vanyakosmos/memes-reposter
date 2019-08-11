import easy_env

CORS_ORIGIN_ALLOW_ALL = easy_env.get_bool('CORS_ORIGIN_ALLOW_ALL', default=False)
CORS_ORIGIN_WHITELIST = [
    easy_env.get('FRONTEND_URL', 'https://localhost:5000'),
]
