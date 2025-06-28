import json
from typing import Optional

import redis
from src.core.config import REDIS_URL

r = redis.Redis.from_url(REDIS_URL)

PUBSUB_CHANNEL = "params_updates"


def publish(event: dict) -> None:
    r.publish(PUBSUB_CHANNEL, json.dumps(event))


def get_message(pubsub) -> Optional[dict]:
    msg = pubsub.get_message()
    if msg and msg["type"] == "message":
        return json.loads(msg["data"])
    return None
