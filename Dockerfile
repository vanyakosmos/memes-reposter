FROM python:3.6

RUN apt-get -y update && apt-get -y install libav-tools

WORKDIR /app

RUN pip install pipenv
COPY ./Pipfile /app
COPY ./Pipfile.lock /app
RUN pipenv install --system --deploy
COPY . /app
# setup required env vars in .env file (SECRET_KEY, tg token...)
RUN python manage.py collectstatic --noinput -v 0
