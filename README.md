# missbot

*WARNING: Very Alpha - not ready to use yet, many things here are not yet done*

This is a composable slack bot framework that can either run standalone with plugins or composed into another [aiohttp](https://docs.aiohttp.org/en/stable/) application.

## Usage

Required Config:

| Name | Required | Purpose |
| :--: | :------: | ------- |
| SLACK_CLIENT_ID | Y | OAuth2 Client ID |
| SLACK_CLIENT_SECRET | Y | OAuth2 Client Secret |
| SLACK_SIGNING_KEY | Y | Shared secret with slack to validate requests |

### Standalone

```bash
$ python3 -m missbot
```

### Composed

```python
from aiohttp import web
from missbot import app_factory as missbot

from .routes import my_routes


# this is your standard aiohttp setup!
async def app_factory():
    app = web.Application()
    app.add_routes(my_routes)

    # add missbot as a subapp
    app.add_subapp("/bot/", await missbot())

    return app
```

## Plugins (incomplete)

A plugin is simply an async function decorated with a `missbot.registry.registry` decorator and type hint what dependencies you have:

```python
from typing import Any, Dict, Optional

from aiohttp import ClientSession

from missbot.registry import registry
from missbot.types import SlashEvent, Redis


@registry.on_slash("/quote")
async def on_slash_quote(event: SlashEvent, client_session: ClientSession, redis: Redis) -> Optional[Dict[str, Any]]:
    """do your work and use the event['response_url'] or return a dict"""
```

## Required Permissions (not started)

To get your app set up with slack, you will need to know what permissions all your plugins require. To get these you can ask missbot:

```bash
$ python3 -m missbot manifest

slash commands:
    COMMAND | PATH
    /quote | /slack/commands/quote
    /chart | /slack/commands/chart
    ...

interactivity & shortcuts
    /slack/shortcuts:
        NAME | LOCATION | CALLBACK ID
        Report Message | Messages | report_message

event subscriptions:
    /slack/events:
        bot:
            - app_mention
            - message.channels
            - pin_adde
            ...

permissions:
    OAuth2 Redirect: /auth/slack/add/callback
    Scopes:
        - app_mentions:read
        - channels:history
        - channels:join
        ...
```

This will generate a manifest for you to define your slack app's required permissions in your developer portal.
