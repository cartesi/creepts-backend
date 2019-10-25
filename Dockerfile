FROM python:3.7-alpine

LABEL mantainer "Carlo Fragni <carlo@cartesi.io>"

ENV BASE=/opt/cartesi/

COPY . $BASE/
WORKDIR $BASE

RUN pip3 install -r requirements.txt

EXPOSE 8000

# Starting server
CMD [ "gunicorn", "-b", "0.0.0.0:8000", "creepts.app:api" ]
