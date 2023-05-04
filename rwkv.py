import requests
import json

url = 'http://10.80.43.125:7888/'


def rwkv(words: str):
    data = {
        "log": words,
        "top_p":  0.5,
        "temperature": 1.1,
        "presence_penalty": 0.3,
        "frequency_penalty": 0.3
    }
    try:
        response = requests.post(url+"chat", json.dumps(data))
        return response.text
    except requests.exceptions.RequestException as e:
        return "抱歉，我无法理解你的问题"


def rwkvreset():
    response = requests.get(url+"reset")
    return response.text
