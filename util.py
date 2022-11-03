import base64
import hashlib
import os
import time

import cbor2
from cryptography.hazmat.primitives import hashes, serialization, padding
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
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
    return base64.b64encode(
        ecies_encryption(receiver_pub_key, cbor2.dumps(obj)))


def decrypt_obj(priv_key, enc_data_b64):
    return cbor2.loads(ecies_decryption(priv_key, base64.b64decode(
        enc_data_b64)))


# def pad(size, data) -> bytes:
#     """
#     :param size: int
#     :param data: bytes
#     :return:
#     """
#     padder = padding.PKCS7(size * 8).padder()
#     return padder.update(data) + padder.finalize()
#
#
# def unpad(size, data) -> bytes:
#     """
#     :param size: int
#     :param data: bytes
#     :return:
#     """
#     unpadder = padding.PKCS7(size * 8).unpadder()
#     return unpadder.update(data) + unpadder.finalize()
#
#
# def encrypt(key, iv, data) -> bytes:
#     """
#     Encrypts data using 'key' as key and 'iv' as initialization vector.
#     :param key: bytes:
#     :param data: bytes:
#     :return:
#     """
#     cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
#     encryptor = cipher.encryptor()
#
#     padded_data = pad(len(key), data)
#     return encryptor.update(padded_data) + encryptor.finalize()
#
#
# def decrypt(key, iv, enc_data) -> bytes:
#     cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
#     decryptor = cipher.decryptor()
#
#     dec_data = decryptor.update(enc_data) + decryptor.finalize()
#
#     return unpad(len(key), dec_data)
#     # return AESOCB3(key).decrypt(iv, enc_data, None)


def encrypt_file(inp_path, out_path, key):
    iv = os.urandom((algorithms.AES(key).block_size) // 8)
    cipher = Cipher(algorithms.AES(key), modes.OFB(iv))
    encryptor = cipher.encryptor()

    with open(inp_path, 'rb') as inp_file, open(out_path, 'wb') as out_file:
        out_file.write(iv)
        buf_size = 1024
        while True:
            data = inp_file.read(buf_size)
            if not data:
                out_file.write(encryptor.finalize())
                break
            out_file.write(encryptor.update(data))


def decrypt_file(inp_path, out_path, key):
    with open(inp_path, 'rb') as inp_file, open(out_path, 'wb') as out_file:
        iv = inp_file.read(algorithms.AES(key).block_size // 8)
        cipher = Cipher(algorithms.AES(key), modes.OFB(iv))
        decryptor = cipher.decryptor()
        buf_size = 1024
        while True:
            enc_data = inp_file.read(buf_size)
            if not enc_data:
                out_file.write(decryptor.finalize())
                break
            out_file.write(decryptor.update(enc_data))


class Timer:
    store = dict()

    def __init__(self, op, *args):
        self._op = op
        self._key = args

    def __enter__(self):
        self._start_time = time.time_ns()

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ns = time.time_ns() - self._start_time

        if self._op not in self.store:
            self.store[self._op] = dict()

        if self._key not in self.store[self._op]:
            self.store[self._op][self._key] = list()

        self.store[self._op][self._key].append(duration_ns)


if __name__ == '__main__':
    key = os.urandom(32)
    encrypt_file('temp/user2', 'temp/user2_enc', key)
    decrypt_file('temp/user2_enc', 'temp/user2_dec', key)
