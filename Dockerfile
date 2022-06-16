FROM python:3.9-slim-buster

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app

CMD gunicorn --workers 3 -b 0.0.0.0:8080 'app:create_app()'