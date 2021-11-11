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
    for _ in range(0):
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
for _ in range(32):
    # init contents
    resp = requests.post(url=API_ENDPOINT1, json=create_list)
    assert(resp.status_code == 200)

    # make sure all replicas have heard about init changes
    time.sleep(2)

    # stress
    t1 = threading.Thread(target=async_req, args=(API_ENDPOINT1,))
    t2 = threading.Thread(target=async_req, args=(API_ENDPOINT2,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # make sure all replicas have heard about all changes
    time.sleep(2)

    # assert equal
    # reminder: maps are unordered
    try:
        read1 = requests.post(url=API_ENDPOINT1, json=read)
        read2 = requests.post(url=API_ENDPOINT2, json=read)
        assert(str(deserialize(bytes(read1.text, 'utf-8'))) ==
               str(deserialize(bytes(read2.text, 'utf-8'))))
        print("passed-all")
    except:
        # make sure failure is not due to network delays
        time.sleep(10)
        read1 = requests.post(url=API_ENDPOINT1, json=read)
        read2 = requests.post(url=API_ENDPOINT2, json=read)
        try:
            assert(str(deserialize(bytes(read1.text, 'utf-8'))) ==
                   str(deserialize(bytes(read2.text, 'utf-8'))))
            print("passed-all")
        except:
            print("failed")
            print(deserialize(bytes(read1.text, 'utf-8')))
            print(deserialize(bytes(read2.text, 'utf-8')))
            break
