FROM python:3-alpine

LABEL mantainer "Carlo Fragni <carlo@cartesi.io>"

ENV BASE=/opt/cartesi/

COPY . $BASE/
WORKDIR $BASE/anuto-server

RUN pip3 install -r requirements_dev.txt

EXPOSE 8000

# Starting server
CMD [ "gunicorn", "-b", "0.0.0.0:8000", "app:api" ]
