import multiprocessing
import os
from datetime import timedelta

import easy_env
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())

PORT = os.environ.get('PORT', '8000')
WEB_WORKERS = easy_env.get_int('WEB_WORKERS', multiprocessing.cpu_count())

bind = ":" + PORT
workers = WEB_WORKERS
timeout = timedelta(minutes=30).seconds

accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s'
