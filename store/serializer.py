import base64
import pickle

# implements a simple serializer for json node trees
# python object (trees) -> serialized binary dump -> base64


def serialize(node):
    return base64.b64encode(pickle.dumps(node)).decode('utf-8')


def deserialize(data):
    return pickle.loads(base64.b64decode(data))
