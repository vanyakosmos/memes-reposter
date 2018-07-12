#!/usr/bin/env bash

if [ ${1:-dev} == 'dev' ]
then
	echo "running dev server..."
	exec python manage.py runserver
else
	echo "running production server..."
	exec gunicorn memes_reposter.wsgi -c server.py
fi
