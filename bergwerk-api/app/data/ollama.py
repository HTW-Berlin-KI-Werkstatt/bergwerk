import requests
import json
from service import config as service_config


def load_model(model):
    url = service_config.get_configitem("ollama_api_url").value + "/api/pull"
    print(url)
    payload = {
        "model": model,
    }

    response = requests.post(url, json=payload)
    return response

def delete_model(model):
    url =  service_config.get_configitem("ollama_api_url").value + "/api/load"
    print(url)
    payload = {
        "model": model,
    }

    response = requests.post(url, json=payload)
    return response

def query_llm(textinput, model):

    url = service_config.get_configitem("ollama_api_url").value + "/api/generate"
    payload = {
        "model": model,
        "stream": False,
        "prompt": textinput
    }

    response = requests.post(url, json=payload)
    to = json.loads(response.text)

    try:
        return to['response']
    except:
        return " "