"""
Integration tests for the server go here
"""
import requests

from store.json_store import ListNodeT, MapNodeT, RegNodeT
from store.serializer import serialize, deserialize

# defining the api-endpoint
API_ENDPOINT = "http://127.0.0.1:5000/"

obj = RegNodeT("listitem1", "1")

# data to be sent to api
data = {
    "type": "insert",
    "cursor": ["map1", "list1"],
    "payload": serialize(obj),
    "args": {
        "insert_type": "insert_at_head",
    }
}

read = {
    "type": "get",
    "cursor": [],
}

# sending post request and saving response as response object
r = requests.post(url=API_ENDPOINT, json=data)
read = requests.post(url=API_ENDPOINT, json=read)
print(deserialize(bytes(r.text, 'utf-8')))
print(deserialize(bytes(read.text, 'utf-8')))
