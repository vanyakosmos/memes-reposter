import multiprocessing

import easy_env


REDIS_URL = easy_env.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TASK_SERIALIZER = 'json'
CELERY_WORKER_CONCURRENCY = easy_env.get_int(
    'CELERY_WORKER_CONCURRENCY', default=multiprocessing.cpu_count()
)
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_REDIS_MAX_CONNECTIONS = 20
