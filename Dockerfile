FROM ubuntu:18.04

MAINTAINER Carlo Fragni <carlo@cartesi.io>

ENV BASE=/opt/cartesi/

COPY . $BASE/
WORKDIR $BASE/anuto-server

# Install python and other dependencies
RUN \
    apt update && \
    apt install -y python3 python3-pip

RUN \
    pip3 install -r requirements_dev.txt

# Starting server
CMD gunicorn -b 0.0.0.0:8000 app:api
