import asyncio
import hmac
import hashlib
import logging
import time

from aiohttp import web

from .middleware import slack_verification_middleware
from .routes import routes

logger = logging.getLogger(__name__)


async def slack_factory(signing_secret: str, registry) -> web.Application:
    app = web.Application(
        middlewares=[
            slack_verification_middleware(signing_secret),
        ]
    )

    app["registry"] = registry

    app.add_routes(routes)

    return app
