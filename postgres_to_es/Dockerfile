# pull official base image
FROM python:3.8-slim as etl

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 5431
EXPOSE 9200

# copy project
COPY . .

# install dependencies
RUN pip install --upgrade pip && pip install -r requirements/prod.txt

RUN python loader.py