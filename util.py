import base64
import hashlib

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes


def hash(*args) -> bytes:
    h = hashlib.sha256()
    for arg in args:
        h.update(arg)

    return h.digest()


def pad(size, data) -> bytes:
    """
    :param size: int:
    :param data: bytes:
    :return:
    """
    padder = padding.PKCS7(size * 8).padder()
    return padder.update(data) + padder.finalize()


def encrypt(key, iv, data) -> bytes:
    """
    Encrypts data using 'key' as key and 'iv' as initialization vector.
    :param key: bytes:
    :param data: bytes:
    :return:
    """
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()

    block_size_bytes = len(key)
    encrypted_data = bytes()
    for i in range(0, len(data) // block_size_bytes):
        encrypted_data += encryptor.update(data[i:i + block_size_bytes])
    rem = len(data) % block_size_bytes
    if rem != 0:
        encrypted_data += encryptor.update(pad(block_size_bytes, data[-rem:]))
    encrypted_data += encryptor.finalize()

    return encrypted_data


