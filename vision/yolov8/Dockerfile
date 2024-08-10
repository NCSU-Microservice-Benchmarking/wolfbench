# 使用 ARM64 架构的 Ubuntu 20.04 作为基础镜像
FROM arm64v8/ubuntu:20.04

LABEL maintainer="Zhouyu Li"
LABEL email="zli85@ncsu.edu"
LABEL version="0.1"
LABEL platform="arm"
LABEL device="cpu"

USER root

# 设置非交互模式以避免在构建过程中出现交互提示
ARG DEBIAN_FRONTEND=noninteractive

# 更新包列表并安装必要的软件包
RUN apt-get update \
    && apt-get install -y ffmpeg libsm6 libxext6 python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件到容器中
COPY . /usr/src/pyserver

# 设置工作目录
WORKDIR /usr/src/pyserver

# 安装Python依赖项
RUN pip3 install -r requirements.txt

# 设置环境变量
ENV FLASK_APP app.py
ENV JAEGER_ENDPOINT http://jaeger-with-cassandra-and-kafka-collector.observability.svc.cluster.local:4318
# Uncomment the following line if testing locally with a Jaeger container
# ENV JAEGER_ENDPOINT http://host.docker.internal:4318

# 暴露容器的端口
EXPOSE 5000

# 设置容器启动时执行的命令
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app", "--timeout", "120"]
