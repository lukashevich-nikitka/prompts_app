FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

WORKDIR /setup

RUN apt-get update && apt-get -y install --no-install-recommends \
    build-essential \
    libpq-dev \
    && pip install poetry==2.0.1 \
    && rm -rf /var/lib/apt/lists/*

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-root

FROM builder AS runtime

WORKDIR /app

COPY . .

RUN chown -R 9000:9000 /app

EXPOSE 8000
USER 9000
