FROM ubuntu:20.04
LABEL authors="petr"

WORKDIR /hg_app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Europe/Prague
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y python3 python3-dev python3-venv python3-pip python3-gdal \
    binutils libproj-dev gdal-bin \
    libsqlite3-mod-spatialite && \
    apt-get clean

RUN pip3 install --upgrade pip

COPY ./requirements.txt /hg_app/requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /hg_app

