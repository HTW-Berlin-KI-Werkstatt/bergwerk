import redis
import json
from model.configuration import ConfigItem

r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

def get_configitem(item: str) -> ConfigItem:

    # Decode bytes and parse JSON if needed
    config_raw = r.hgetall("config:app")
    config = {}
    for key, val in config_raw.items():
        try:
            config[key] = json.loads(val)
        except json.JSONDecodeError:
            print(f"Decode error in key {key}")
            config[key] = val

    return ConfigItem(key=item, value=config[item])


