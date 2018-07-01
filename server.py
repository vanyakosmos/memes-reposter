import multiprocessing
import os
from datetime import timedelta


PORT = os.environ.get('PORT', '8000')

bind = ":" + PORT
workers = multiprocessing.cpu_count()
timeout = timedelta(minutes=30).seconds

accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s'
