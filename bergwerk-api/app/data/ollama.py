import requests
import json
from data import redis as data_redis


def load_model(model):
    url = data_redis.get_configitem("ollama_api_url").value + "/api/load"
    payload = {
        "model": model,
    }

    response = requests.post(url, json=payload)
    return response

def delete_model(model):
    url =  data_redis.get_configitem("ollama_api_url").value + "/api/load"
    payload = {
        "model": model,
    }

    response = requests.post(url, json=payload)
    return response

def query_llm(textinput, model):

    url = data_redis.get_configitem("ollama_api_url").value + "/api/generate"
    payload = {
        "model": model,
        "stream": False,
        "prompt": textinput
    }

    response = requests.post(url, json=payload)
    to = json.loads(response.text)

    return to['response']
