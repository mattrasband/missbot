import asyncio
import logging

from aiohttp import ClientSession, web

from missbot.types import BotToken, Redis, SlashEvent

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


@routes.post("/events", name="on_slack_event")
async def on_slack_event(req: web.Request):
    """handle all events from the slack event hook api"""
    body = await req.json()
    logger.debug("received event: %s", body)
    if (evt_type := body.get("type")) :
        if evt_type == "url_verification":
            return web.json_response({"challenge": body["challenge"]})
        elif evt_type == "event_callback":
            asyncio.create_task(req.app["registry"].delegate(body))
            return web.json_response({})

    logger.warning("unhandled slack event: %s", body)
    return web.json_response({})


@routes.post("/commands/{command}", name="on_slack_command")
async def on_slack_command(req: web.Request) -> web.Response:
    """handle all the slack slash commands"""
    # token, team_id, team_domain, channel_id, channel_name,
    # user_id, user_name, command, text, api_app_id,
    # response_url, trigger_id
    body = await req.post()
    logger.debug("received command: %s", body)
    bot_token = await req.config_dict["redis"].hmget(body["team_id"], "token", encoding="utf-8")
    result = await req.app["registry"].exec_slash(
        body,
        {
            BotToken: bot_token[0] if bot_token else None,
            Redis: req.config_dict["redis"],
            SlashEvent: body,
            ClientSession: req.config_dict["client_session"],
        },
    )
    if result:
        return web.json_response(result)
    return web.Response()
