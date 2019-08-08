#!/usr/bin/env bash

if [[ ${1:-dev} == 'dev' ]]
then
	echo "running dev server..."
	exec python manage.py runserver 0.0.0.0:8000
else
	echo "running production server..."
	exec gunicorn application.wsgi -c server.py
fi
