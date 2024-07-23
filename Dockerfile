FROM python:3.12.3-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install libpq-dev -y

RUN python -m venv /venv

ENV PATH="/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .