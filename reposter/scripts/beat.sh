#!/usr/bin/env bash

exec celery -A application.celery beat -l ${1:-info}
