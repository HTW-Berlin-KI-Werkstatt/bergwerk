import redis
import json
from model.configuration import ConfigItem

r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True, encoding="utf-8")

def get_configitem(item: str) -> ConfigItem:
    val = r.hget("config:app", item)
    try:
        value = json.loads(val)
    except (TypeError, json.JSONDecodeError):
        value = val
    return ConfigItem(key=item, value=value)

