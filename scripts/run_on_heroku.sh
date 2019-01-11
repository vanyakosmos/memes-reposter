#!/usr/bin/env bash

set -e

gunicorn memes_reposter.wsgi -c server.py &
celery -A memes_reposter.celery beat -l info &
exec celery -A memes_reposter.celery worker -l info
