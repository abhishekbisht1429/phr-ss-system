import hashlib


def hash(*args) -> bytes:
    h = hashlib.sha256()
    for arg in args:
        h.update(arg)

    return h.digest()