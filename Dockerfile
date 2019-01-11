FROM python:3.6

RUN apt-get -y update && apt-get -y install libav-tools

WORKDIR /app

RUN pip install pipenv
COPY ./Pipfile /app
COPY ./Pipfile.lock /app
RUN pipenv install --system --deploy
COPY . /app

ARG SECRET_KEY
ARG TELEGRAM_BOT_TOKEN
ENV SECRET_KEY "$SECRET_KEY"
ENV TELEGRAM_BOT_TOKEN "$TELEGRAM_BOT_TOKEN"
RUN python manage.py collectstatic --noinput -v 0
