from queue import Queue
import threading

import requests
from execution.operations import Operation
from store.serializer import serialize
from util.command_parser import CommandLineArgs
from util.config_reader import ConfigReader
from util.logger import Logger


class ReceiverQueue:
    # simple thread safe queue for buffering incoming replica operations

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
    # send network queue
    # asynchronously sends buffered send requests to replicas

    def __init__(self):
        super().__init__()
        self.log = Logger()
        self.config = ConfigReader()

    def _start(self):
        # update replica ip list here
        # filter to not send requests to self
        ENDPOINTS = list(
            filter(lambda endpoint: endpoint, self.config.get("peers")))

        while True:
            op = self.pop()
            if op:
                for API_ENDPOINT in ENDPOINTS:
                    r = requests.post(url=API_ENDPOINT +
                                      "/replicate", json=serialize(op))
                    self.log.info("sent_operation_to_replica: status: ",
                                  r.status_code, "operation: ", op, "replica: ", API_ENDPOINT)

    def start(self):
        self.log.info("peers_list: ", self.config.get("peers"))
        t = threading.Thread(target=self._start)
        t.start()
