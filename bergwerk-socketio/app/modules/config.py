import requests
from icecream import ic
import redis 

r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True, encoding="utf-8")

class Config:

    def __init__(self):
        self.config = {}

    def get_value(self, k):
        value = r.hget("config:app", k)
        if value is None:
            raise KeyError(f"Key '{k}' not found in config:app")
        return value.replace("\\n\\n", "\n\n")
