import os
import shelve
from constants import STORE_KEY_MASTER_KEY
from config import current_head_store_path


with shelve.open(current_head_store_path) as store:
    if STORE_KEY_MASTER_KEY not in store:
        store[STORE_KEY_MASTER_KEY] = os.urandom(32)

    global master_key
    master_key = store[STORE_KEY_MASTER_KEY]



