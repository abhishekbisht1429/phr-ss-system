import base64
import hashlib
import os

import cbor2
from cryptography.hazmat.primitives import padding, serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
import time

from cryptography.hazmat.primitives.ciphers.aead import AESOCB3
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def b64s_to_bytes(s):
    """
    converts a base64 string to bytes
    :param s:
    :return:
    """
    return base64.b64decode(s.encode('utf-8'))


def bytes_to_b64s(data) -> str:
    """
    :param data:
    :return:
    """
    return base64.b64encode(data).decode('utf-8')


def hash(*args) -> bytes:
    h = hashlib.sha256()
    for arg in args:
        h.update(arg)

    return h.digest()


def pad(size, data) -> bytes:
    """
    :param size: int
    :param data: bytes
    :return:
    """
    padder = padding.PKCS7(size * 8).padder()
    return padder.update(data) + padder.finalize()


def unpad(size, data) -> bytes:
    """
    :param size: int
    :param data: bytes
    :return:
    """
    unpadder = padding.PKCS7(size * 8).unpadder()
    return unpadder.update(data) + unpadder.finalize()


def encrypt(key, iv, data) -> bytes:
    """
    Encrypts data using 'key' as key and 'iv' as initialization vector.
    :param key: bytes:
    :param data: bytes:
    :return:
    """
    # cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    # encryptor = cipher.encryptor()

    # padded_data = pad(len(key), data)
    return AESOCB3(key).encrypt(iv, data, None)
    # return encryptor.update(padded_data) + encryptor.finalize()


def decrypt(key, iv, enc_data) -> bytes:
    # cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    # decryptor = cipher.decryptor()
    #
    # dec_data = decryptor.update(enc_data) + decryptor.finalize()

    # return unpad(len(key), dec_data)
    return AESOCB3(key).decrypt(iv, enc_data, None)


def time_stamp():
    time_int = time.time_ns()
    return time_int.to_bytes(8, byteorder='big')


def to_base64(data) -> str:
    """

    :param data, bytes:
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


def encrypt_obj(pub_key, obj):
    return base64.b64encode(ecies_encryption(pub_key, cbor2.dumps(obj)))


def decrypt_obj(priv_key, enc_data_b64):
    return cbor2.loads(ecies_decryption(priv_key, base64.b64decode(
        enc_data_b64)))
