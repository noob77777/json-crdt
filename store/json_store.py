import random
import string
from lamport.lamport import LamportCounter
from execution.operations import Operation, OperationType
from util.logger import Logger


class Node:
    # basic node for json tree

    def __init__(self, id, last_modified=LamportCounter(), list_index=-1, tombstone=False):
        self.id = id
        self.last_modified = last_modified
        self.tombstone = tombstone
        self.list_index = list_index
        self.children = dict()

    # recursively set the last modified for entire subtree
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
    # register nodes contain simple values -> (string, boolean, null, number)
    # supports only string for now

    def __init__(self, id, value, last_modified=LamportCounter(), list_index=-1, tombstone=False):
        super().__init__(id, last_modified, list_index, tombstone)
        self.value = value

    def __str__(self):
        return "( id: " + self.id + " :: " + self.value + " )"

    def assign(self, node):
        pass


class ListNodeT(Node):
    # json list node type

    ID_LENGTH = 32

    def __init__(self, id, last_modified=LamportCounter(), list_index=-1, tombstone=False):
        super().__init__(id, last_modified, list_index, tombstone)

    def __str__(self):
        s = ""
        st_list = []
        for id in self.children:
            if not self.children[id].tombstone:
                st_list.append(self.children[id])
        st_list.sort(key=lambda node: node.list_index)
        for node in st_list:
            s += " " + node.id + " : " + str(node)
        s = s.lstrip()
        return "[ id: " + self.id + " :: " + s + " ]"

    @staticmethod
    # generate a random id for children as unlike maps list doesn't have
    # well defined keys for the chilren and using indices violates crdt properties
    def get_random_id():
        return ''.join(random.choice(string.ascii_uppercase + string.digits)
                       for _ in range(ListNodeT.ID_LENGTH))

    def assign(self, node):
        # assign only if node already present and has same index
        if node.id in self.children and self.children[node.id].list_index == node.list_index:
            return super().assign(node)

    def insert_at_head(self, node):
        # head is always at list_index 0
        node.list_index = 0

        # id should be unique
        if not node.id in self.children:
            # increment list_indices for all nodes
            for id in self.children:
                self.children[id].list_index += 1
            self.children[node.id] = node

    def insert_after(self, id, node):
        # insert_after id should be present
        if id in self.children:
            # list index for node is next to list_index for node with 'id' id
            node.list_index = self.children[id].list_index + 1

            # increment list_index of all nodes after the insertion point
            for _id in self.children:
                if self.children[_id].list_index > self.children[id].list_index:
                    self.children[_id].list_index += 1
            self.children[node.id] = node

    def delete(self, id):
        # node should be present
        if id in self.children and not self.children[id].tombstone:
            index = self.children[id].list_index
            for _id in self.children:
                # decrement indices for nodes after deletion point
                if self.children[_id].list_index > index:
                    self.children[_id].list_index -= 1
            self.children[id].tombstone = True

            # this makes sense
            self.children[id].list_index -= 1


class MapNodeT(Node):
    # json map node type

    def __init__(self, id, last_modified=LamportCounter(), list_index=-1, tombstone=False):
        super().__init__(id, last_modified, list_index, tombstone)

    def __str__(self):
        s = ""
        for id in self.children:
            if not self.children[id].tombstone:
                s += " " + id + " : " + str(self.children[id])
        s = s.lstrip()
        return "{ id: " + self.id + " :: " + s + " }"


class Store:
    # local state store, not persistent
    # implements core crdt logic
    # conflict rule - last writer wins

    def __init__(self):
        self.root = MapNodeT("doc", LamportCounter())
        self.log = Logger()

    def __str__(self):
        return "{ " + str(self.root) + " }"

    @staticmethod
    # traverse the json tree
    def recursive_get(node, timestamp, cursor, index):
        if len(cursor) == index:
            return node

        # only allowed to visit child if the following are satisfied
        # 1. child_id is valid
        # 2. child is not marked deleted i.e. tombstoned
        # 3. last_modified timestamp is "earlier" than current timestamp (no time travel queries)
        if cursor[index] in node.children and not node.children[cursor[index]].tombstone and not node.children[cursor[index]].last_modified > timestamp:
            return Store.recursive_get(node.children[cursor[index]], timestamp, cursor, index + 1)
        else:
            return None

    def get(self, timestamp, cursor):
        return Store.recursive_get(self.root, timestamp, cursor, 0)

    def execute(self, operation: Operation):
        # we need to delete the node from its parent so only traverse till parent
        delete_id = None
        if operation.type == OperationType.DELETE:
            delete_id = operation.cursor.pop()

        # node should be reachable
        node = self.get(operation.id, operation.cursor)
        if node:
            if operation.type == OperationType.ASSIGN:
                # we can always assign a new node
                if not operation.payload.id in node.children:
                    node.assign(operation.payload)
                    return operation.payload
                # updates only if last_modified is not in future
                elif node.children[operation.payload.id].last_modified < operation.id:
                    node.assign(operation.payload)
                    return operation.payload
                else:
                    self.log.info("assignment_restricted: ", operation)
                    return None

            if operation.type == OperationType.INSERT:
                # always a valid insert if arguments are valid
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
                    self.log.info("insertion_failed: ", operation)
                    return None

            if operation.type == OperationType.DELETE:
                if not delete_id in node.children:
                    return None
                # delete only if last_modified is not in future
                elif node.children[delete_id].last_modified < operation.id:
                    node.delete(delete_id)
                    node.children[delete_id].last_modified = operation.id
                    return delete_id
                else:
                    self.log.info("deletion_restricted: ", operation)
                    return None

            # gets are read only so...
            if operation.type == OperationType.GET:
                return node

        else:
            self.log.info("tree_traversal_restricted: ", operation)
            return None
