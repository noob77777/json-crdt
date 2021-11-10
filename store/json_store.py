import random
import string
from lamport.lamport import LamportCounter
from execution.operations import Operation, OperationType


class Node:
    def __init__(self, id, last_modified=LamportCounter(), list_index=-1, tombstone=False):
        self.id = id
        self.last_modified = last_modified
        self.tombstone = tombstone
        self.list_index = list_index
        self.children = dict()

    def set_last_modified(self, last_modified):
        self.last_modified = last_modified
        for id in self.children:
            self.children[id].set_last_modified(last_modified)

    def delete(self, id):
        if id in self.children:
            self.children[id].tombstone = True

    def assign(self, node):
        self.children[node.id] = node


class RegNodeT(Node):
    def __init__(self, id, value, last_modified=LamportCounter(), list_index=-1, tombstone=False):
        super().__init__(id, last_modified, list_index, tombstone)
        self.value = value

    def __str__(self):
        return "( id: " + self.id + " :: " + self.value + " )"


class ListNodeT(Node):
    ID_LENGTH = 32

    def __init__(self, id, last_modified=LamportCounter(), list_index=-1, tombstone=False):
        super().__init__(id, last_modified, list_index, tombstone)

    def __str__(self):
        s = ""
        for id in self.children:
            s += " " + id + " : " + str(self.children[id])
        s = s.lstrip()
        return "[ id: " + self.id + " :: " + s + " ]"

    def get_random_id():
        ''.join(random.choice(string.ascii_uppercase + string.digits)
                for _ in range(ListNodeT.ID_LENGTH))

    def assign(self, node):
        if node.id in self.children and self.children[node.id].list_index == node.list_index:
            return super().assign(node)

    def insert_at_head(self, node):
        node.list_index = 0
        if node.id not in self.children:
            for id in self.children:
                self.children[id].list_index += 1
            self.children[node.id] = node

    def insert_after(self, id, node):
        if id in self.children:
            node.list_index = self.children[id].list_index + 1
            for _id in self.children:
                if self.children[_id].list_index > node.list_index:
                    self.children[_id].list_index += 1
            self.children[node.id] = node

    def delete(self, id):
        if id in self.children and not self.children[id].tombstone:
            index = self.children[id].list_index
            for _id in self.children:
                if self.children[_id].list_index > index:
                    self.children[_id].list_index -= 1
            self.children[id].tombstone = True
            self.children[id].list_index -= 1


class MapNodeT(Node):
    def __init__(self, id, last_modified=LamportCounter(), list_index=-1, tombstone=False):
        super().__init__(id, last_modified, list_index, tombstone)

    def __str__(self):
        s = ""
        for id in self.children:
            s += " " + id + " : " + str(self.children[id])
        s = s.lstrip()
        return "{ id: " + self.id + " :: " + s + " }"


class Store:
    def __init__(self):
        self.root = MapNodeT("doc", LamportCounter())

    def __str__(self):
        return "{ " + str(self.root) + " }"

    @staticmethod
    def recursive_get(node, timestamp, cursor, index):
        if len(cursor) == index:
            return node

        if cursor[index] in node.children and not node.children[cursor[index]].tombstone and not node.children[cursor[index]].last_modified > timestamp:
            return Store.recursive_get(node.children[cursor[index]], timestamp, cursor, index + 1)
        else:
            return None

    def get(self, timestamp, cursor):
        return Store.recursive_get(self.root, timestamp, cursor, 0)

    def execute(self, operation: Operation):
        delete_id = None
        if operation.type == OperationType.DELETE:
            delete_id = operation.cursor.pop()

        node = self.get(operation.id, operation.cursor)
        if node:
            if operation.type == OperationType.ASSIGN:
                if operation.payload.id not in node.children:
                    node.assign(operation.payload)
                    return operation.payload
                elif node.children[operation.payload.id].last_modified < operation.id:
                    node.assign(operation.payload)
                    return operation.payload
                else:
                    return None

            if operation.type == OperationType.INSERT:
                insert_type = operation.args["insert_type"]
                insert_id = None
                if insert_type == "insert_after":
                    insert_id = operation.args["insert_id"]
                if insert_type == "insert_at_head":
                    node.insert_at_head(operation.payload)
                    return operation.payload
                elif insert_type == "insert_after":
                    node.insert_after(insert_id, operation.payload)
                    return operation.payload
                else:
                    return None

            if operation.type == OperationType.DELETE:
                if delete_id not in node.children:
                    return None
                elif node.children[delete_id].last_modified < operation.id:
                    node.delete(delete_id)
                    node.children[delete_id].last_modified = operation.id
                    return delete_id
                else:
                    return None

            if operation.type == OperationType.GET:
                return node

        else:
            return None
