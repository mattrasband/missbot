import hashlib
import hmac
import logging
import time

from aiohttp import web

logger = logging.getLogger(__name__)


def slack_verification_middleware(signing_secret: str, timeout: int = 60 * 5):
    @web.middleware
    async def middleware(req: web.Request, handler):
        if (signature := req.headers.get("X-Slack-Signature")) :
            logger.debug("validating slack signature")
            if time.time() - (ts := int(req.headers.get("X-Slack-Request-Timestamp"))) < timeout:
                digest = hmac.new(
                    signing_secret.encode(),
                    ":".join(
                        [
                            "v0",
                            str(ts),
                            await req.text(),
                        ]
                    ).encode(),
                    hashlib.sha256,
                ).hexdigest()

                if hmac.compare_digest("v0=" + digest, signature):
                    logger.debug("slack signature verified, continuing request chain")
                    return await handler(req)
            else:
                logger.error("slack request timestamp is old, ignoring")

        raise web.HTTPForbidden()

    return middleware
