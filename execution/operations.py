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
    def __init__(self, id, dependecies, cursor, remote, type, payload=None, args=None):
        self.id = id
        self.dependecies = list(dependecies)
        self.cursor = list(cursor)
        self.remote = remote
        self.type = type
        self.payload = payload
        self.args = args

    def __str__(self):
        s = "{ " + "id: " + str(self.id) + " " + "deps: " + str(self.dependecies) + " " + "cursor: " + \
            str(self.cursor) + " " + "type: " + str(self.type) + \
            " " + "args: " + str(self.args) + " }"
        return s
