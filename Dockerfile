FROM python:3.6

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

RUN SECRET_KEY=temp-secret-key python manage.py collectstatic --noinput -v 0
COPY . /app
