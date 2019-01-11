#!/usr/bin/env bash

set -e

python manage.py migrate

if [[ ${1:-dev} == 'dev' ]]
then
    echo "🛠"
	echo "🛠  running DEV server"
	echo "🛠"
	exec python manage.py runserver 0.0.0.0:8000
else
    echo "🎬"
	echo "🎬  running PROD server"
	echo "🎬"
	exec gunicorn memes_reposter.wsgi -c server.py
fi
