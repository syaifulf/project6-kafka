FROM python:3.8

RUN apt update -y

RUN apt install default-jdk -y

COPY requirements.txt requirements.txt

COPY . project

RUN pip install -r requirements.txt

