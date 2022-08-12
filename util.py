import base64
import hashlib
import os

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
import time

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
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()

    padded_data = pad(len(key), data)
    return encryptor.update(padded_data) + encryptor.finalize()


def decrypt(key, iv, enc_data) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()

    dec_data = decryptor.update(enc_data) + decryptor.finalize()

    return unpad(len(key), dec_data)


def time_stamp():
    time_int = time.time_ns()
    return time_int.to_bytes(8, byteorder='big')


def bytes_to_base64(data) -> str:
    """

    :param data, bytes:
    :return:
    """

    return base64.b64encode(data).decode('utf-8')

def b64_to_bytes(s):
    """
    converts a base64 string to bytes
    :param s:
    :return:
    """
    return base64.b64decode(s.encode('utf-8'))

# if __name__ == '__main__':
#     key = os.urandom(32)
#     iv = os.urandom(16)
#
#     # padded_data = pad(len(key), b'hello hello hello asdfadfadfafddafads')
#     # print('padded', padded_data)
#     #
#     # print('unpadded', unpad(len(key), padded_data))
#
#     enc_data = encrypt(key, iv, b'1')
#     print(enc_data)
#
#     data = decrypt(key, iv, enc_data)
#     print(data)
