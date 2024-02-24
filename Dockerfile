FROM python:3.11-slim

WORKDIR /app-bot

ENV PYTHONUNBUFFERED=1 \
		PYTHONDOWNTWRITEBYTECODE=1

COPY requirements.txt /app-bot/

RUN apt-get update && \
    apt-get clean && \
		pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
		apt-get remove -y gcc && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY . /app-bot/