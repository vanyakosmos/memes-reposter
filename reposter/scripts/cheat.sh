#!/usr/bin/env bash

nohup gunicorn application.wsgi -c server.py &
nohup celery -A application.celery beat -l info &
exec celery -A application.celery worker -l info
