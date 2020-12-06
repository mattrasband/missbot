from aiohttp import web

from .slack import routes as slack_routes


async def auth_factory() -> web.Application:
    app = web.Application()

    app.add_routes(slack_routes)

    return app
