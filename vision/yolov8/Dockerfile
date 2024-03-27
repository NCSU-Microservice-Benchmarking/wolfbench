FROM nvidia/cuda:12.3.2-runtime-ubuntu22.04

LABEL maintainer="Zhouyu Li"
LABEL email="zli85@ncsu.edu"
LABEL version="0.1"
LABEL platform="x86_64"
LABEL device="cpu"

USER root

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt install -y ffmpeg libsm6 libxext6
RUN apt install -y python3 python3-pip

COPY . /usr/src/pyserver

WORKDIR /usr/src/pyserver

RUN pip install -r requirements.txt

RUN export FLASK_APP=app.py

ENV JAEGER_ENDPOINT http://jaeger-with-cassandra-and-kafka-collector.observability.svc.cluster.local:4318
# Uncomment the following line if testing locally with a Jaeger container
# ENV JAEGER_ENDPOINT http://host.docker.internal:4318

EXPOSE 5000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app", "--timeout", "120"]