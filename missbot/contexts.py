import aioredis
from aiohttp import ClientSession, web
from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def apscheduler_ctx(app: web.Application):
    scheduler = AsyncIOScheduler()
    app["scheduler"] = scheduler
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown()


async def client_session_ctx(app: web.Application):
    async with ClientSession(raise_for_status=True) as cs:
        app["client_session"] = cs
        yield


def redis_ctx_factory(url: str, *, minsize=5, maxsize=10):
    async def redis_ctx(app: web.Application):
        redis = await aioredis.create_redis_pool(url, minsize=minsize, maxsize=maxsize)
        app["redis"] = redis
        try:
            yield
        finally:
            redis.close()
            await redis.wait_closed()

    return redis_ctx
