FROM python:3.6

RUN apt-get -y update && apt-get -y install libav-tools

WORKDIR /app

RUN pip install pipenv
COPY ./requirements.txt /app
RUN pip install -r requirements.txt
COPY . /app
