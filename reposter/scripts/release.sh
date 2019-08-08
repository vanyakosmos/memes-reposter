#!/usr/bin/env bash

python manage.py migrate
python manage.py collectstatic --noinput -v 0
