import re

from aiohttp import ClientSession

from missbot.registry import registry
from missbot.types import SlashEvent
from missbot.configutil import load_secret


@registry.on_slash("/chart")
async def on_slash_chart(command: SlashEvent, client_session: ClientSession):
    pass


@registry.on_slash("/quote")
async def on_slash_quote(command: SlashEvent, client_session: ClientSession):
    if (td_client_id := load_secret("td_client_id")) :
        symbols = []
        cryptos = []
        for match in re.finditer(r"\b(?P<prefix>c:)?(?P<symbol>[A-z]+)\b", command["text"]):
            if match.group("prefix") == "c:":
                cryptos.append(match.group("symbol"))
            else:
                symbols.append(match.group("symbol"))
        print("cryptos:", cryptos)

        if symbols:
            async with client_session.get(
                f"https://api.tdameritrade.com/v1/marketdata/quotes",
                params={"apikey": td_client_id, "symbol": ",".join(symbols)},
            ) as r:
                quotes = await r.json()

            if not quotes:
                return {
                    "response_type": "ephemeral",
                    "text": f"Sorry, I couldn't find any quotes for {', '.join(symbols)}.",
                }

            blocks = []
            for symbol, quote in quotes.items():
                direction = "upwards" if quote["netPercentChangeInDouble"] >= 0 else "downwards"
                blocks.extend(
                    [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f":chart_with_{direction}_trend: *{symbol}*: ${quote['mark']:,.2f} ({quote['netPercentChangeInDouble']:,.2f}%) :chart_with_{direction}_trend:",
                            },
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"52wk Low: ${quote['52WkLow']:,.2f}",
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"52wk High: ${quote['52WkHigh']:,.2f}",
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"Open: ${quote['openPrice']:,.2f}",
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"Close: ${quote['closePrice']:,.2f}",
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"High: ${quote['highPrice']:,.2f}",
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"Low: ${quote['lowPrice']:,.2f}",
                                },
                            ],
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "text": quote["description"]
                                    + f" | <!date^{int(quote['quoteTimeInLong']/1000)}^Quote as of {{date_long}} {{time_secs}}|{int(quote['quoteTimeInLong']/1000)}>",
                                    "type": "mrkdwn",
                                },
                            ],
                        },
                    ]
                )

            block = {
                "response_type": "in_channel",
                "blocks": blocks,
            }

            async with client_session.post(command["response_url"], json=block) as r:
                await r.text()

        else:
            return {
                "response_type": "ephemeral",
                "text": f"Sorry, I couldn't find any symbols in the command.",
            }
    else:
        return {
            "response_type": "ephemeral",
            "text": "Sorry, this slash command is misconfigured. Please alert the developer!",
        }
