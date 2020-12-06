import argparse
import logging
import os

from aiohttp import ClientSession, web

from .auth import auth_factory
from .contexts import (
    client_session_ctx,
    redis_ctx_factory,
)
from .slack import slack_factory
from .registry import registry

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


async def app_factory() -> web.Application:
    app = web.Application(middlewares=[])

    # TODO: command (and links) to generate required permissions
    app.update(
        {
            "SLACK_CLIENT_ID": os.getenv("SLACK_CLIENT_ID"),
            "SLACK_CLIENT_SECRET": os.getenv("SLACK_CLIENT_SECRET"),
            # TODO: in config, generate set of required user scopes...
            "SLACK_USER_SCOPES": [],
            # TODO: in config, generate set of required slack bot scopes...
            "SLACK_BOT_SCOPES": [
                "app_mentions:read",
                "channels:history",
                "channels:join",
                "channels:read",
                "chat:write",
                "commands",
                "files:read",
                "files:write",
                "groups:history",
                "groups:read",
                "im:history",
                "im:read",
                "pins:read",
                "pins:write",
                "reactions:read",
                "reactions:write",
                "team:read",
                "users:read",
            ],
        }
    )

    app.cleanup_ctx.extend(
        [
            client_session_ctx,
            redis_ctx_factory(os.getenv("REDIS_URL")),
        ]
    )

    app.add_subapp("/auth/", await auth_factory())
    app.add_subapp(
        "/slack/",
        await slack_factory(os.getenv("SLACK_SIGNING_SECRET"), registry=registry),
    )

    return app
