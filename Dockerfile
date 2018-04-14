FROM python:3.6

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app

ENV DEBUG 0
EXPOSE 5000

CMD ["python", "index.py"]
