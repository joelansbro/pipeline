# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY ./API.py .
COPY ./celeryBroker.py .
COPY ./cleanjob.py .
COPY ./config.py .
COPY ./DAO.py .
COPY ./intakejob.py .
COPY ./keywordjob.py .
COPY ./pipe_utils.py .
COPY ./reportjob.py .

CMD ["python3", "API.py"]



