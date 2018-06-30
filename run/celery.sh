#!/usr/bin/env bash

exec celery -A memes_reposter.celery worker -B -c 1 --autoscale 1 -l ${1:-info}
