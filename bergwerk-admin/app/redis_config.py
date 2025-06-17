import redis
import json

r = redis.Redis(host='redis', port=6379, decode_responses=True, db=0)

def get_all_config():

    # Decode bytes and parse JSON if needed
    config_raw = r.hgetall("config:app")
    config = {}
    for key, val in config_raw.items():
        try:
            config[key] = json.loads(val)
        except json.JSONDecodeError:
            print(f"Decode error in key {key}")
            config[key] = val

    return config

def update_config(new_data):
    for k, v in new_data.items():
        # Store as JSON string for consistency
        r.hset("config:app", k, json.dumps(v))
