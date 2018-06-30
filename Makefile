reset:
	rm db.sqlite3
	./manage.py makemigrations
	./manage.py migrate
	./manage.py createsuperuser --username admin --email admin@admin.org

mig:
	./manage.py makemigrations
	./manage.py migrate
