FROM python:3-alpine AS base

WORKDIR /app
RUN apk add --no-cache gcc g++ make libffi-dev
COPY requirements ./requirements/
RUN pip install -r requirements/production.txt
EXPOSE 8080
CMD gunicorn missbot:app_factory --bind 0.0.0.0:8080 --worker-class aiohttp.GunicornUVLoopWebWorker

FROM base AS dev
RUN pip install -r requirements/development.txt
RUN pip install tox
COPY . .
CMD gunicorn missbot:app_factory \
    --bind 0.0.0.0:8080 \
    --worker-class aiohttp.GunicornUVLoopWebWorker \
    --reload

FROM base as prod
COPY . .
USER missbot
