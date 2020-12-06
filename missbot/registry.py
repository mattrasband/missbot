import asyncio
import logging
import re
from functools import wraps

logger = logging.getLogger(__name__)


class Registry:
    __slots__ = (
        "event_handlers",
        "command_handlers",
    )

    def __init__(self):
        self.event_handlers = {}
        self.command_handlers = {}

    async def exec_command(self, command):
        # TODO: typing.get_type_hints(include_extras=True)
        if (handler := self.command_handlers.get(command["command"])) :
            return await handler(command)

    def command(self, name: str):
        if not name.startswith("/"):
            name = "/" + name

        def wrapper(f):
            if not asyncio.iscoroutinefunction(f):
                raise ValueError(f"{f.__name__} is not a coroutine")
            if (h := self.command_handlers.get(name)) :
                raise ValueError(f"{name} already has a registered handler '{h.__name__}'")
            self.command_handlers[name] = f
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

    def on_event(self, name: str, *, regex=None, test=None):
        if regex is not None and test is not None:
            raise ValueError("cannot have both a regex and test func")

        def wrapper(f):
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


registry = Registry()


@registry.on_event("message", regex=re.compile(r"\bhi\b"))
async def handle_message(event):
    print("handle hi only")


@registry.on_app_mention
async def on_app_mention(event):
    print("on_app_mention")


@registry.on_message
async def handle_message_2(event):
    print("handle 2")


@registry.command("/quote")
async def on_command_quote(command):
    print("command:", command["command"])
