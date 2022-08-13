import os
import shelve
import sys

from cryptography.hazmat.primitives import serialization

import constants
from config import keystore_path, hs_public_key_path
from cryptography.hazmat.primitives.asymmetric import ec
import util

with shelve.open(keystore_path) as store:
    # Generate or load master key
    if constants.STORE_KEY_MASTER not in store:
        store[constants.STORE_KEY_MASTER] = os.urandom(32)

    global master_key
    master_key = store[constants.STORE_KEY_MASTER]

    # Generate or Load EC public private key pairs
    if constants.STORE_KEY_EC_PRIVATE not in store:
        _ec_private_key = ec.generate_private_key(ec.SECP256R1())
        _ec_public_key = _ec_private_key.public_key()

        serialized_private_key = _ec_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(
                b'some password')
        )
        serialized_public_key = _ec_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        store[constants.STORE_KEY_EC_PRIVATE] = serialized_private_key
        store[constants.STORE_KEY_EC_PUBLIC] = serialized_public_key

    _ec_private_key = serialization.load_pem_private_key(
        store[constants.STORE_KEY_EC_PRIVATE],
        b'some password'
    )

    _ec_public_key = serialization.load_pem_public_key(
        store[constants.STORE_KEY_EC_PUBLIC]
    )

    _ec_public_key_sz = store[constants.STORE_KEY_EC_PUBLIC]

    # if STORE_KEY_EC_PRIVATE not in store:
    #     _ec_private_key = ec.generate_private_key(ec.SECP256R1())
    #     _ec_private_value = _ec_private_key.private_numbers().private_value
    #
    #     # save values in keystore
    #     _ec_private_bytes = _ec_private_value.to_bytes(
    #         util.byte_len(_ec_private_value), sys.byteorder)
    #
    #     store[STORE_KEY_EC_PRIVATE] = _ec_private_bytes
    #
    # _ec_private_bytes = store[STORE_KEY_EC_PRIVATE]
    # _ec_private_value = int.from_bytes(_ec_private_bytes, sys.byteorder)
    # _ec_private_key = ec.derive_private_key(_ec_private_value, ec.SECP256R1())

# Load the hospital public key
with open(hs_public_key_path, 'r') as hs_public_key_file:
    _hs_public_key = serialization.load_pem_public_key(
        hs_public_key_file.read().encode('utf-8')
    )


def public_key():
    return _ec_public_key


def public_key_sz():
    return _ec_public_key_sz


def private_key():
    return _ec_private_key


def hs_public_key():
    return _hs_public_key