FROM python:3-alpine AS base

WORKDIR /app
RUN apk add --no-cache gcc g++ make libffi-dev tzdata && \
    cp /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "UTC" >> /etc/timezone
COPY requirements ./requirements/
RUN pip install -r requirements/production.txt
RUN adduser missbot --disabled-password --no-create-home
EXPOSE 8080
CMD gunicorn missbot:app_factory --bind 0.0.0.0:8080 --worker-class aiohttp.GunicornUVLoopWebWorker

FROM base AS dev
RUN pip install -r requirements/development.txt
RUN pip install tox watchdog[watchmedo]
COPY . .
CMD gunicorn missbot:app_factory \
    --bind 0.0.0.0:8080 \
    --worker-class aiohttp.GunicornUVLoopWebWorker \
    --reload

FROM base as prod
COPY . .
USER missbot
