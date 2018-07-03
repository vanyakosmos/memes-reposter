#!/usr/bin/env bash

exec celery -A memes_reposter.celery worker -B -c 4 -l ${1:-info}
