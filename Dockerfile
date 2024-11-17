FROM python:3.10-slim

WORKDIR /app

RUN apt-get update &&  \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip

COPY ./requirements.txt ./requirements.txt
RUN python3 -m pip install -r requirements.txt

COPY . .
RUN pip install -e .
