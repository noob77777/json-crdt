import base64
import pickle


def serialize(node):
    return base64.b64encode(pickle.dumps(node))


def deserialize(data):
    return pickle.loads(base64.b64decode(data))
