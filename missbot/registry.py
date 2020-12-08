import asyncio
import logging
import os
import re
from functools import wraps
from typing import Any, Dict, List, Optional, get_type_hints

from aiohttp import ClientSession

from .configutil import load_secret
from .types import BotToken, SlashEvent, Redis

logger = logging.getLogger(__name__)


class _Registry:
    __slots__ = (
        "event_handlers",
        "slash_handlers",
    )

    def __init__(self):
        self.event_handlers = {}
        self.slash_handlers = {}

    async def exec_slash(self, command, providers: Dict[Any, Any]):
        if (handler := self.slash_handlers.get(command["command"])) :
            types = get_type_hints(handler, include_extras=True)
            #  logger.debug(
            #      "handler %s expects types %s, available types: %s",
            #      handler.__name__,
            #      types,
            #      providers,
            #  )
            kwargs = {}
            for param, type_ in types.items():
                if (t := providers.get(type_)) :
                    kwargs[param] = t
                else:
                    logger.warning(
                        "unable to provide %s (type: %s) to %s", param, type_, handler.__name__
                    )

            return await handler(**kwargs)

    def on_slash(self, name: str):
        if not name.startswith("/"):
            name = "/" + name

        def wrapper(f):
            logger.debug("registering %s for %s", f.__name__, name)
            if not asyncio.iscoroutinefunction(f):
                raise ValueError(f"{f.__name__} is not a coroutine")
            if (h := self.slash_handlers.get(name)) :
                raise ValueError(f"{name} already has a registered handler '{h.__name__}'")
            self.slash_handlers[name] = f
            return f

        return wrapper

    async def delegate(self, event):
        logger.debug("delegating event: %s", event["event"]["type"])
        for h in self.event_handlers.get(event["event"]["type"], []):
            asyncio.create_task(self._delegator(h, event))

    async def _delegater(self, func, event):
        # TODO: typing.get_type_hints(include_extras=True)
        if (v := func.__missbot_test__(event["event"]["text"])) :
            return await func(event, v)

    def on_event(
        self,
        name: str,
        *,
        regex: Optional[re.Pattern] = None,
        test=None,
        scopes: Optional[List[str]] = None,
    ):
        if regex is not None and test is not None:
            raise ValueError("cannot have both a regex and test func")

        def wrapper(f):
            logger.debug("add event handler %s for %s", f.__name__, name)

            if not asyncio.iscoroutinefunction(f):
                raise ValueError(f"{f.__name__} is not a coroutine")

            if regex is not None:
                f.__missbot_test__ = regex.search
            elif test is not None:
                f.__missbot_test__ = test
            else:
                f.__missbot_test__ = lambda *args, **kwargs: True

            if name in self.event_handlers:
                self.event_handlers[name].append(f)
            else:
                self.event_handlers[name] = [f]

            return f

        return wrapper

    def on_app_mention(self, f):
        return self.on_event("app_mention")(f)

    def on_message(self, f):
        # TODO: support matcher as func or regex
        return self.on_event("message")(f)


registry = _Registry()


@registry.on_event("message", regex=re.compile(r"\bhi\b"))
async def handle_message(event):
    print("handle hi only")


@registry.on_app_mention
async def on_app_mention(event):
    print("on_app_mention")


@registry.on_message
async def handle_message_2(event):
    print("handle 2")
