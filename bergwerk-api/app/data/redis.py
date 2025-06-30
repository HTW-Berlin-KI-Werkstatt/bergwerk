import redis
import json
from model.configuration import ConfigItem

r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True, encoding="utf-8")

def get_configitem(item: str) -> ConfigItem:
    config_raw = r.hgetall("config:app")
    config = {}
    for key, val in config_raw.items():
        try:
            config[key] = json.loads(val)
        except json.JSONDecodeError:
            print(f"Decode error in key {key}")
            config[key] = val
    return ConfigItem(key=item, value=config[item])

def get_all_config():
    config_raw = r.hgetall("config:app")
    config = {}
    for key, val in config_raw.items():
        config[key] = val
    return config
