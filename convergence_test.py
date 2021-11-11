"""
Convergence stress tests for the server go here
"""
import random
import requests
import threading
import time

from store.json_store import ListNodeT, MapNodeT, RegNodeT
from store.serializer import serialize, deserialize

# defining the api-endpoints
API_ENDPOINT1 = "http://127.0.0.1:5000/"
API_ENDPOINT2 = "http://127.0.0.1:5001/"


def async_req(endpoint):
    for _ in range(256):
        data = {
            "type": "assign",
            "cursor": [],
            "payload": serialize(RegNodeT("reg", str(random.random()))),
        }
        r = requests.post(url=endpoint, json=data)
        assert(r.status_code == 200)


read = {
    "type": "get",
    "cursor": [],
}
while True:
    # stress
    t1 = threading.Thread(target=async_req, args=(API_ENDPOINT1,))
    t2 = threading.Thread(target=async_req, args=(API_ENDPOINT2,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # make sure all replicas have heard about all changes
    time.sleep(10)

    # assert equal
    read1 = requests.post(url=API_ENDPOINT1, json=read)
    read2 = requests.post(url=API_ENDPOINT2, json=read)
    print(deserialize(bytes(read1.text, 'utf-8')))
    print(deserialize(bytes(read2.text, 'utf-8')))
    assert(str(deserialize(bytes(read1.text, 'utf-8'))) ==
           str(deserialize(bytes(read2.text, 'utf-8'))))
