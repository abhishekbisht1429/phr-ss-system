import base64
import hashlib


def hash(*args) -> bytes:
    h = hashlib.sha256()
    for arg in args:
        h.update(arg)

    return h.digest()


def b64_to_bytes(s):
    """
    converts a base64 string to bytes
    :param s:
    :return:
    """
    return base64.b64decode(s.encode('utf-8'))


def bytes_to_b64(data) -> str:
    """
    :param data:
    :return:
    """
    return base64.b64encode(data).decode('utf-8')

