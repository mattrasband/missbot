from aiohttp import web
from yarl import URL


def redirect_uri(req: web.Request, callback_name: str) -> str:
    port = None
    if (p := req.url.port) not in [80, 443]:
        port = p

    return str(
        URL.build(
            scheme=req.url.scheme,
            host=req.url.host,
            port=port,
            path=str(req.app.router[callback_name].url_for()),
        )
    )
