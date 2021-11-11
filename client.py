"""
Integration tests for the server go here
"""
import requests

from store.json_store import ListNodeT, MapNodeT, RegNodeT
from store.serializer import serialize, deserialize

# defining the api-endpoint
API_ENDPOINT = "http://127.0.0.1:5001/"

# data to be sent to api
data = {
    "type": "get",
    "cursor": [],
    "payload": serialize(MapNodeT("map1")),
}

# data = {
#     "type": "insert",
#     "cursor": ["list"],
#     "payload": serialize(RegNodeT(ListNodeT.get_random_id(), "uwu")),
#     "args": {
#         "insert_type": "insert_after",
#         "insert_id": "XZYR5DA2FRJ6PX6BLOAETTR8YG79Y5QG"
#     }
# }

read = {
    "type": "get",
    "cursor": [],
}

# sending post request and saving response as response object
r = requests.post(url=API_ENDPOINT, json=data)
read = requests.post(url=API_ENDPOINT, json=read)
print(deserialize(bytes(r.text, 'utf-8')))
print(deserialize(bytes(read.text, 'utf-8')))
