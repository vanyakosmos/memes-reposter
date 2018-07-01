#!/usr/bin/env bash

if [ ${2:-1} -eq 1 ]
then
	python manage.py migrate
	python manage.py collectstatic --noinput -v 0
fi

if [ ${1:-dev} == 'dev' ]
then
	echo "running dev server..."
	exec python manage.py runserver
else
	echo "running production server..."
	exec gunicorn memes_reposter.wsgi -c server.py
fi
