import encodings
import os
import shelve
import hashlib
from client_keys import master_key
from constants import CURRENT_HEAD_STORE
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


def __hash(*args) -> bytes:
    h = hashlib.sha256()
    for arg in args:
        h.update(arg)

    return h.digest()


def __pad(size, data) -> bytes:
    """
    :param size: int:
    :param data: bytes:
    :return:
    """
    padder = padding.PKCS7(size * 8).padder()
    return padder.update(data) + padder.finalize()


def __encrypt(key, iv, data) -> bytes:
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
        encrypted_data += encryptor.update(__pad(block_size_bytes, data[-rem:]))
    encrypted_data += encryptor.finalize()

    return encrypted_data


def gen_secure_index(keywords, fid) -> (dict, bytes):
    """
    :param keywords: list:
    :param fid: bytes:
    :return:
    """
    secure_index = dict()
    iv = os.urandom(16)
    for w in keywords:
        kw = __hash(master_key, w.encode(encoding='utf-8'))
        addr = __hash(kw, fid, b'0')
        key = __hash(kw, fid, b'1')

        # generate address and key of previous head
        with shelve.open(CURRENT_HEAD_STORE) as store:
            # TODO: find appropriate name replacement for prev_addr and prev_key
            if w not in store:
                store[w] = b'some representation of null'
            prev_fid = store[w]
            prev_addr = __hash(kw, prev_fid, b'0')
            prev_key = __hash(kw, prev_fid, b'1')

            enc_fid = __encrypt(key, iv, fid)
            enc_prev_addr = __encrypt(key, iv, prev_addr)
            enc_prev_key = __encrypt(key, iv, prev_key)

            # An entry in secure index
            secure_index[addr] = (enc_fid, enc_prev_addr, enc_prev_key, iv)

            # Update the current head store
            store[w] = fid

    return secure_index


if __name__ == '__main__':
    keywords = ['hello', 'this', 'is', 'a', 'demo']
    print(gen_secure_index(keywords, b'file1'))
