import base64
import hashlib
import os

import cbor2
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESOCB3
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


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


def ecies_encryption(receiver_pub_key, data):
    cipher_priv_key = ec.generate_private_key(ec.SECP256R1())
    cipher_pub_key = cipher_priv_key.public_key()
    nonce = os.urandom(12)
    shared_key = cipher_priv_key.exchange(ec.ECDH(), receiver_pub_key)
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=nonce,
        info=None
    ).derive(shared_key)

    cipher_pub_key_sz = cipher_pub_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    cipher = AESOCB3(derived_key).encrypt(nonce, data, None)

    return cbor2.dumps([cipher_pub_key_sz, cipher, nonce])


def ecies_decryption(recv_priv_key, cipher):
    cipher_pub_key_sz, cipher, nonce = cbor2.loads(cipher)
    cipher_pub_key = serialization.load_pem_public_key(cipher_pub_key_sz)
    shared_key = recv_priv_key.exchange(ec.ECDH(), cipher_pub_key)
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=nonce,
        info=None
    ).derive(shared_key)

    data = AESOCB3(derived_key).decrypt(nonce, cipher, None)

    return data


def encrypt_obj(receiver_pub_key, obj):
    """
    :param receiver_pub_key: 
    :param obj: 
    :return: 
    """
    return base64.b64encode(ecies_encryption(receiver_pub_key, cbor2.dumps(obj)))


def decrypt_obj(priv_key, enc_data_b64):
    return cbor2.loads(ecies_decryption(priv_key, base64.b64decode(
        enc_data_b64)))

