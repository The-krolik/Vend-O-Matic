# syntax=docker/dockerfile:1

FROM python:3.10.6-slim-buster

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

WORKDIR /Vend-O-Matic

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD [ "python3", "-m", "flask", "--app=vendomatic.py", "run"] 
