import shelve

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

import constants
from config import keystore_path

with shelve.open(keystore_path) as store:
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

        # store the public key in a file
        with open('./temp/server_pub_key', 'wb') as file:
            file.write(serialized_public_key)

    _ec_private_key = serialization.load_pem_private_key(
        store[constants.STORE_KEY_EC_PRIVATE],
        b'some password'
    )

    _ec_public_key = serialization.load_pem_public_key(
        store[constants.STORE_KEY_EC_PUBLIC]
    )

    _serialized_public_key = store[constants.STORE_KEY_EC_PUBLIC]
    _serialized_private_key = store[constants.STORE_KEY_EC_PRIVATE]


def server_ec_pub_key():
    return _ec_public_key


def server_ec_priv_key():
    return _ec_private_key


def serialized_pub_key():
    return _serialized_public_key

