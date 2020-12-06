import logging

from aiohttp import web
from missbot import app_factory

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


def main():
    # TODO:
    #  1. proper CLI for a few things, one of which is generating a "manifest"
    #     that would inform anyone that uses this bot framework of how to configure
    #     the slack UI
    #  2. add support for required roles
    # dependency injection via type annotations?
    import uvloop

    uvloop.install()

    parser = argparse.ArgumentParser()
    # parser.add_argument("config", help="config file path", type=str)
    args = parser.parse_args()

    web.run_app(app_factory(), host="0.0.0.0", port=8080, shutdown_timeout=30)


if __name__ == "__main__":
    main()
