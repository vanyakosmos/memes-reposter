#!/usr/bin/env bash

set -e

gunicorn reposter.wsgi -c server.py &
celery -A reposter.celery beat -l info &
exec celery -A reposter.celery worker -l info
