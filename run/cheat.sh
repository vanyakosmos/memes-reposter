#!/usr/bin/env bash

nohup gunicorn memes_reposter.wsgi -c server.py &
nohup celery -A memes_reposter.celery beat -l info &
exec celery -A memes_reposter.celery worker -l info
