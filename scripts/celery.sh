#!/usr/bin/env bash

exec celery -A memes_reposter.celery worker -l ${1:-info} -c ${2:-2} -B
