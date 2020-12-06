import uuid

from aiohttp import web
from yarl import URL

from .util import redirect_uri


routes = web.RouteTableDef()


# @routes.get("/slack", name="slack_authorize")
# async def slack_authorize(req: web.Request) -> web.Response:
#     query = {
#         "client_id": req.config_dict["SLACK_CLIENT_ID"],
#         "redirect_uri": redirect_uri(req, "slack_callback"),
#         "state": str(uuid.uuid4()),
#         "user_scope": " ".join(["identity.basic", "identity.avatar"]),
#     }
#     raise web.HTTPFound(
#         location=URL("https://slack.com/oauth/v2/authorize").with_query(query)
#     )
#
#
# @routes.get("/slack/callback", name="slack_callback")
# async def slack_callback(req: web.Request) -> web.Response:
#     if (code := req.query.get("code")):
#         async with req.config_dict["client_session"].get(
#             "https://slack.com/api/oauth.v2.access",
#             params={
#                 "client_id": req.config_dict["SLACK_CLIENT_ID"],
#                 "client_secret": req.config_dict["SLACK_CLIENT_SECRET"],
#                 "code": code,
#                 "redirect_uri": redirect_uri(req, "slack_callback"),
#             },
#             headers={"Accept": "application/json"},
#         ) as r:
#             # ok, app_id, authed_user: { id, scope, access_token, token_type },
#             # scope, token_type, access_token, bot_user_id, team: { id, name },
#             # enterprise: ?
#             at = await r.json()
#             print("access_token:", at)
#         # TODO: render template that redirects so the user knows what's up.
#         raise web.HTTPFound(location=URL.build(
#             scheme="slack",
#             host="app",
#             query={"team": at["team"]["id"], "id": at["app_id"], "tab": "messages"},
#         ))
#     else:
#         return web.json_response({}, status=401)


@routes.get("/slack/add", name="add_to_slack")
async def add_to_slack(req: web.Request) -> web.Response:
    """Kick off the oauth2 flow (which is actually installing a slack app)"""
    query = {
        "client_id": req.config_dict["SLACK_CLIENT_ID"],
        "redirect_uri": redirect_uri(req, "add_to_slack_callback"),
        "state": str(uuid.uuid4()),
    }
    if (bot_scopes := req.config_dict.get("SLACK_BOT_SCOPES")) :
        query["scope"] = " ".join(bot_scopes)
    if (user_scopes := req.config_dict.get("SLACK_USER_SCOPES")) :
        query["user_scope"] = " ".join(user_scopes)
    raise web.HTTPFound(location=URL("https://slack.com/oauth/v2/authorize").with_query(query))


@routes.get("/slack/add/callback", name="add_to_slack_callback")
async def slack_callback(req: web.Request) -> web.Response:
    """Handle the oauth2 callback, finalizing the slack install"""
    q = req.url.query

    if (code := q.get("code")) :
        async with req.config_dict["client_session"].post(
            "https://slack.com/api/oauth.v2.access",
            data={
                "client_id": req.config_dict["SLACK_CLIENT_ID"],
                "client_secret": req.config_dict["SLACK_CLIENT_SECRET"],
                "code": code,
                "redirect_uri": redirect_uri(req, "add_to_slack_callback"),
            },
            headers={"Accept": "application/json"},
        ) as r:
            # ok, app_id, authed_user: { id, scope, access_token, token_type },
            # scope, token_type, access_token, bot_user_id, team: { id, name },
            # enterprise: ?
            at = await r.json()
            if at["ok"]:
                # TODO: move to helper funcs
                await req.config_dict["redis"].hmset(at["team"]["id"], "token", at["access_token"])
        # TODO: render template that redirects so the user knows what's up.
        raise web.HTTPFound(
            location=URL.build(
                scheme="slack",
                host="app",
                query={"team": at["team"]["id"], "id": at["app_id"], "tab": "messages"},
            )
        )
    else:
        return web.json_response({}, status=401)
