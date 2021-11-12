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
API_ENDPOINTS = ["http://127.0.0.1:5000", "http://127.0.0.1:5001"]

# fixed queries
create_list = {
    "type": "assign",
    "cursor": [],
    "payload": serialize(ListNodeT("list"))
}
read = {
    "type": "get",
    "cursor": [],
}


def async_req(endpoint):
    # set a register/map
    for _ in range(32):
        data = {
            "type": "assign",
            "cursor": [],
            "payload": serialize(RegNodeT("reg", random.random())),
        }
        r = requests.post(url=endpoint, json=data)
        assert(r.status_code == 200)

    # list insert and delele
    for _ in range(32):
        # insert_at_head
        id = ListNodeT.get_random_id()
        data = {
            "type": "insert",
            "cursor": ["list"],
            "payload": serialize(RegNodeT(id, random.random())),
            "args": {
                "insert_type": "insert_at_head"
            }
        }
        r = requests.post(url=endpoint, json=data)
        assert(r.status_code == 200)

        # insert_after
        data = {
            "type": "insert",
            "cursor": ["list"],
            "payload": serialize(RegNodeT(ListNodeT.get_random_id(), random.random())),
            "args": {
                "insert_type": "insert_after",
                "insert_id": id,
            }
        }
        r = requests.post(url=endpoint, json=data)
        assert(r.status_code == 200)

        # delete
        data = {
            "type": "delete",
            "cursor": ["list", id]
        }
        r = requests.post(url=endpoint, json=data)
        assert(r.status_code == 200)


# recommended: loop more than once
for _ in range(16):
    # init contents
    resp = requests.post(url=API_ENDPOINTS[0], json=create_list)
    assert(resp.status_code == 200)

    # make sure all replicas have heard about init changes
    time.sleep(2)

    # stress
    threads = list(map(lambda endpoint: threading.Thread(
        target=async_req, args=(endpoint,)), API_ENDPOINTS))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # make sure all replicas have heard about all changes
    time.sleep(2)

    # assert equal
    # reminder: maps are unordered
    try:
        reads = list(map(lambda endpoint: str(deserialize(bytes(requests.post(
            url=endpoint, json=read).text, 'utf-8'))), API_ENDPOINTS))
        unique = set(reads)
        assert(len(unique) == 1)
        print("passed-all")
    except:
        # make sure failure is not due to network delays
        time.sleep(10)
        try:
            reads = list(map(lambda endpoint: str(deserialize(bytes(requests.post(
                url=endpoint, json=read).text, 'utf-8'))), API_ENDPOINTS))
            unique = set(reads)
            assert(len(unique) == 1)
            print("passed-all")
        except:
            print("failed")
            for read in reads:
                print(read)
            break
