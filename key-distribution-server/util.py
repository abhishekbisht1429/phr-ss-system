import pickle
import base64


def serialize_obj(obj):
    return base64.b64encode(pickle.dumps(obj))


def deserialize_obj(sz_bytes):
    return pickle.loads(base64.b64decode(sz_bytes))