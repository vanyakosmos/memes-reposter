#!/usr/bin/env bash

set -e

python manage.py migrate
python manage.py collectstatic --noinput -v 0
