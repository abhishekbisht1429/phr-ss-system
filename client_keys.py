import os
import shelve
from constants import STORE_KEY_MASTER_KEY, CURRENT_HEAD_STORE


with shelve.open(CURRENT_HEAD_STORE) as store:
    if STORE_KEY_MASTER_KEY not in store:
        store[STORE_KEY_MASTER_KEY] = os.urandom(32)

    global master_key
    master_key = store[STORE_KEY_MASTER_KEY]



