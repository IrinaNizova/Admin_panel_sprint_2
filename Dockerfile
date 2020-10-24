# pull official base image
FROM python:3.8-slim as movies_admin

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# install dependencies
COPY . .
RUN pip install -U pip && pip install -r requirements/prod.txt

