FROM cartesi/machine-emulator:0.1.0-alpine as emulator

FROM python:3.7-alpine as builder

LABEL mantainer "Carlo Fragni <carlo@cartesi.io>"

# install dev packages
RUN apk add --no-cache openssl musl-dev python3-dev gcc g++ libc-dev

ENV BASE=/opt/cartesi/
WORKDIR $BASE

ENV PATH=/root/.local/bin:$PATH

# install requirements
COPY requirements.txt .
RUN GRPC_PYTHON_BUILD_EXT_COMPILER_JOBS=$(nproc) pip3 install --user -r requirements.txt

# generating grpc-interface python files
COPY ./grpc-interfaces /root/grpc-interfaces
RUN \
    mkdir -p /root/grpc-interfaces/out && \
    cd /root/grpc-interfaces && \
    python3 -m grpc_tools.protoc -I. --python_out=./out --grpc_python_out=./out \
    cartesi-base.proto logger-high.proto && \
    touch ./out/__init__.py && \
    2to3 -w -n ./out

FROM python:3.7.5-alpine3.10

# install dockerize, as we need to wait on the contract address to be extracted
RUN apk add --no-cache openssl libstdc++ brotli

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# copy emulator file (we need cartesi-machine-hash)
COPY --from=emulator /opt/cartesi /opt/cartesi

# copy (compiled) dependencies
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:/opt/cartesi/bin:$PATH

ENV BASE=/opt/cartesi
WORKDIR $BASE/creepts

# copy application
COPY . .
COPY packlog $BASE/bin/
COPY unpacklog $BASE/bin/

# copy gRPC generated code
COPY --from=builder /root/grpc-interfaces/out/*_pb2*.py creepts/logger/

ENV DISPATCHER_HOST=dispatcher
ENV DISPATCHER_PORT=3001
ENV DISPATCHER_TIMEOUT=360s
ENV TIMEOUT=120s

EXPOSE 8000

ENTRYPOINT [ "/opt/cartesi/creepts/entrypoint.sh" ]

# Server command
# CMD [ "gunicorn", "--worker-tmp-dir", "/dev/shm", "--workers=4", "--threads=4", "--worker-class=gthread", "--log-file=-", "-b", "0.0.0.0:8000", "creepts.app:api" ]
CMD [ "gunicorn", "-b", "0.0.0.0:8000", "creepts.app:api" ]
