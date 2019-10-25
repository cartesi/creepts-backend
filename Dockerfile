FROM python:3.7-alpine

LABEL mantainer "Carlo Fragni <carlo@cartesi.io>"

ENV BASE=/opt/cartesi/
WORKDIR $BASE

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . $BASE/

EXPOSE 8000

# Starting server
CMD [ "gunicorn", "-b", "0.0.0.0:8000", "creepts.app:api" ]
