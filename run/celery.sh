#!/usr/bin/env bash

nohup celery -A memes_reposter.celery beat -l info &
exec celery -A memes_reposter.celery worker -c 4 -l ${1:-info}
