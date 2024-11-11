FROM python:3.10-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    locales \
    locales-all \
    postgresql \
    libnss3 \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
    
RUN python -m pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir && rm -f requirements.txt

COPY . .

EXPOSE 8000

ENV PYTHONPATH=.
