from queue import Queue
import threading

import requests
from execution.operations import Operation
from store.serializer import serialize


class ReceiverQueue:
    def __init__(self):
        self.q = Queue()

    def push(self, operation: Operation):
        self.q.put(operation)

    def pop(self):
        if self.q.empty():
            return None
        else:
            return self.q.get()


class SenderQueue(ReceiverQueue):
    def __init__(self):
        super().__init__()

    def _start(self):
        ENDPOINTS = []
        while True:
            op = self.pop()
            if op:
                for API_ENDPOINT in ENDPOINTS:
                    requests.post(url=API_ENDPOINT, json=serialize(op))

    def start(self):
        t = threading.Thread(target=self._start)
        t.start()
