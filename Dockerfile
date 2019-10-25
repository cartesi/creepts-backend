FROM python:3.7-alpine

LABEL mantainer "Carlo Fragni <carlo@cartesi.io>"

# install dockerize
RUN apk add --no-cache openssl
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz

ENV BASE=/opt/cartesi/
WORKDIR $BASE

# install requirements
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# copy application
COPY . $BASE/

EXPOSE 8000

# Starting server
CMD [ "gunicorn", "-b", "0.0.0.0:8000", "creepts.app:api" ]

# wait for dispatcher to be available before starting gunicorn
ENTRYPOINT [ "dockerize", "-wait", "tcp://dispatcher:3001" ]
