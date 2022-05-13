# Dockerfile, Image, Container
# Dockerfile is blueprint for creating images
# Image is blueprint for running containers
# Container the actual running process


FROM python:3.10

WORKDIR /app

COPY requirements.txt requirements.txt

run pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m", "runjob.py" "--host=0.0.0.0" ]


# command
# docker run --publish 8000:5000 python-docker