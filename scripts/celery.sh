#!/usr/bin/env bash

exec celery -A reposter.celery worker -l ${1:-info} -c ${2:-2} -B
