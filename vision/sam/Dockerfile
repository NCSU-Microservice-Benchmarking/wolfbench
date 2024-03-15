FROM bitnami/pytorch:latest

LABEL maintainer="Zhouyu Li"
LABEL email="zli85@ncsu.edu"
LABEL version="0.1"
LABEL platform="x86_64"
LABEL device="cpu"

USER root

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt install -y ffmpeg libsm6 libxext6

COPY . /usr/src/pyserver

WORKDIR /usr/src/pyserver

RUN pip install -r requirements.txt

RUN export FLASK_APP=app.py

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app", "--timeout", "120"]
# CMD gunicorn -w 4 -b 0.0.0.0:5000 app:app
