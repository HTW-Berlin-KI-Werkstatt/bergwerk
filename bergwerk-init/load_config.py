import yaml
import redis
import json
import secrets

def generate_secret_key(length=64):
    return secrets.token_hex(length // 2)

def init_config(yaml_path="config.yaml", redis_host="redis"):
    with open(yaml_path, 'r') as file:
        raw_config = yaml.safe_load(file)

    config = {}
    for key, value in raw_config.items():
        if isinstance(value, (list, dict)):
            config[key] = json.dumps(value)
        else:
            config[key] = str(value)

    secrets = {}
    secrets['secret_key'] = generate_secret_key()


    r = redis.Redis(host=redis_host, port=6379, db=0)

    r.hset("config:app", mapping=config)
    r.hset("config:sec", mapping=secrets)
    print(f"Loaded config into Redis: {config}")

    print("Generated secret key:", secrets['secret_key'])


if __name__ == "__main__":
    try:
        init_config()
    except:
        print("Warning: config.yaml file not found. Trying config.yaml.example.")
        init_config(yaml_path="config.yaml.example")
