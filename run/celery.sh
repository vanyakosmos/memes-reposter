#!/usr/bin/env bash

nohup celery -A memes_reposter.celery beat -l ${1:-info} &
exec celery -A memes_reposter.celery worker -l ${1:-info}
