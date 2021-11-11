"""
Simple client for manual tests
"""
import requests

from store.json_store import ListNodeT, MapNodeT, RegNodeT
from store.serializer import serialize, deserialize

# defining the api-endpoint
API_ENDPOINT = "http://127.0.0.1:5000/"

# data to be sent to api
data = {
    "type": "assign",
    "cursor": [],
    "payload": serialize(RegNodeT("reg", "1")),
}

# data = {
#     "type": "insert",
#     "cursor": ["map", "list"],
#     "payload": serialize(RegNodeT(ListNodeT.get_random_id(), "onichan")),
#     "args": {
#         "insert_type": "insert_at_head",
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
