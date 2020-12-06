import argparse
import logging
import os

from aiohttp import ClientSession, web
from aiohttp_remotes import (
    setup as remotes_setup,
    Secure,
    ForwardedRelaxed,
    XForwardedRelaxed,
)

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

    remotes = [ForwardedRelaxed(), XForwardedRelaxed()]
    if os.getenv("REQUIRE_SSL", "").lower() in ["yes", "true", "1", "on"]:
        remotes.append(Secure())

    await remotes_setup(app, *remotes)

    # TODO: command (and links) to generate required permissions
    app.update(
        {
            "SLACK_CLIENT_ID": _load_secret("slack_client_id"),
            "SLACK_CLIENT_SECRET": _load_secret("slack_client_secret"),
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
            redis_ctx_factory(_load_secret("REDIS_URL")),
        ]
    )

    app.add_subapp("/auth/", await auth_factory())
    app.add_subapp(
        "/slack/",
        await slack_factory(_load_secret("slack_signing_secret"), registry=registry),
    )

    return app


def _load_secret(name):
    """load a secret first attempting the environment then falling back to
    the runtime secrets path at /run/secrets/name.lower()"""
    if (v := os.getenv(name.upper())) :
        return v

    path = f"/run/secrets/{name.lower()}"
    if os.path.exists(path):
        with open(path) as f:
            return f.read().strip()
    raise SystemExit(f"Unable to load secret from env as {name.upper()} or /run/secrets/{name}")
