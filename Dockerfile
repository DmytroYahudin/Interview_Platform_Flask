FROM python:3.10-buster

# WORKDIR /user/src/flask_interview
WORKDIR /app

COPY . .
RUN pip install -r requirements.txt

ENV FLASK_APP="manage.py"

EXPOSE 5000