#!/usr/bin/env bash

#nohup celery -A memes_reposter.celery beat -l info &
exec celery -A memes_reposter.celery worker -l ${1:-info} -B -P solo
