FROM arm32v7/python:3.7-slim-buster

LABEL maintainer="Zhouyu Li"
LABEL email="zli85@ncsu.edu"
LABEL version="0.1"
LABEL platform="arm"
LABEL device="cpu"

USER root

ARG DEBIAN_FRONTEND=noninteractive

COPY . /usr/src/pyserver

WORKDIR /usr/src/pyserver

RUN pip install -r requirements.txt

ENV FLASK_APP app.py
ENV JAEGER_ENDPOINT http://jaeger-with-cassandra-and-kafka-collector.observability.svc.cluster.local:4318
# Uncomment the following line if testing locally with a Jaeger container
# ENV JAEGER_ENDPOINT http://host.docker.internal:4318

EXPOSE 5000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app", "--timeout", "120"]