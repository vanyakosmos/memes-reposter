#!/usr/bin/env bash

exec celery -A application.celery worker -l ${1:-info}
