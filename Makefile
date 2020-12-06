.PHONY: devserver, test

devserver:
	@gunicorn missbot:app_factory --bind 127.0.0.1:8080 --worker-class aiohttp.GunicornUVLoopWebWorker --reload


test:
	@tox
