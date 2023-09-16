import requests

url = "http://localhost:8000/chat"

params = {
    "system_message": "Assume the role of a friendly advisor",
    "human_message": "Compose a 10-point marketing strategy to sell a new product",
}

with requests.post(url, params=params, stream=True) as r:
    for chunk in r.iter_content(None, decode_unicode=True):
        if chunk:
            print(chunk, end="", flush=True)
