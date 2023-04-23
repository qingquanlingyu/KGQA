import requests
import json


def rwkv(words: str):
    url = 'http://127.0.0.1:7888/chat'
    data = {
        "log": words,
        "top_p":  0.2,
        "temperature": 0.8,
        "presence_penalty": 0.2,
        "frequency_penalty": 0.2
    }

    response = requests.post(url, json.dumps(data))
    if response.status_code == 200:
        return response.text
    else:
        return "抱歉，我无法理解你的问题"


def rwkvreset():
    url = 'http://127.0.0.1:7888/reset'
    response = requests.get(url)
    return response.text
