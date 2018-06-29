#!/usr/bin/env bash

exec celery -A rss2tg.celery worker -B -c 1 --autoscale 1 -l ${1:-info}
