.PHONY: devserver, test, envrc, redis_no_port, redis, redis_cli, test_port, korgn, python3

compose: export COMPOSE_DOCKER_CLI_BUILD=1
compose:
	 docker-compose up --build

devserver:
	@gunicorn missbot:app_factory --bind 127.0.0.1:8080 --worker-class aiohttp.GunicornUVLoopWebWorker --reload

test:
	@tox

envrc:
	cat .envrc | grep "export " | sed -E 's/^export ([^=]+)=.*$$/\1/'

redis_no_port:
	docker run --rm -it --name redis redis:6-alpine

redis:
	docker run --rm -it --name redis -p 6379:6379 redis:6-alpine

redis_cli:
	docker run --rm -it --network container:redis redis:6-alpine redis-cli

test_port:
	nc -z 127.0.0.1 $(PORT)

korgn:
	ssh -R 8080:localhost:8080 -N -p 2222 rasband.io

python3:
	docker run --rm -it -v "$(pwd):/app" --workdir /app python:3-alpine sh

