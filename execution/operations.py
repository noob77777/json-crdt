from enum import Enum


class OperationType(Enum):
    GET = 1
    ASSIGN = 2
    INSERT = 3
    DELETE = 5


class RemoteType(Enum):
    CLIENT_API = 1
    REPLICA = 2


class Operation:
    # operation defination for execution

    def __init__(self, id, dependecies, cursor, remote, type, payload=None, args=None):
        self.id = id   # lamport timestamp
        self.dependecies = list(dependecies)
        self.cursor = list(cursor)  # path in json tree
        self.remote = remote  # is_remote boolean
        self.type = type  # GET | ASSIGN | INSERT | DELETE
        self.payload = payload
        self.args = args  # additional arguments required for insertion

    def __str__(self):
        s = "{ " + "id: " + str(self.id) + " " + "deps: " + str(list(map(str, self.dependecies))) + " " + "cursor: " + \
            str(self.cursor) + " " + "type: " + str(self.type) + " " + "payload: " + str(self.payload) + \
            " " + "args: " + str(self.args) + " }"
        return s
