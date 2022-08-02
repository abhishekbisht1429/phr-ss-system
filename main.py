import base64
import os
import shelve
import hashlib
from client_keys import master_key
from config import current_head_store_path
import requests
from util import hash, encrypt


def gen_entries(keywords, fid) -> dict:
    """
    :param keywords: list:
    :param fid: bytes:
    :return:
    """
    secure_index = dict()
    iv = os.urandom(16)
    for w in keywords:
        kw = hash(master_key, w.encode(encoding='utf-8'))
        addr = hash(kw, fid, b'0')
        key = hash(kw, fid, b'1')

        # generate address and key of previous head
        with shelve.open(current_head_store_path) as store:
            # TODO: find appropriate name replacement for prev_addr and prev_key
            if w not in store:
                store[w] = b'some representation of null'
            prev_fid = store[w]
            prev_addr = hash(kw, prev_fid, b'0')
            prev_key = hash(kw, prev_fid, b'1')

            enc_val = encrypt(key, iv, prev_addr + prev_key + fid)

            # An entry in secure index
            secure_index[addr] = (enc_val, iv)

            # Update the current head store
            store[w] = fid

    return secure_index


def request_phr(phr_gen_url, entries_url, doc_id, user_id, passwd):
    """
    Request generation of PHR from doctor
    :return:
    """
    # convert the user_id and password into base64 encoding to send over the
    # network
    user_id_b64 = base64.b64encode(user_id.encode('utf-8'))
    passwd_b64 = base64.b64encode(passwd.encode('utf-8'))
    doc_id_b64 = base64.b64encode(doc_id.encode('utf-8'))

    res = requests.post(phr_gen_url, data={'user_id': user_id_b64,
                                           'passwd': passwd_b64,
                                           'doc_id': doc_id_b64})

    if res.status_code == requests.codes.ok:
        data = res.json()
        phr_id = data['phr_id']
        keywords = data['keywords']

        # generate the encrypted entries
        entries = gen_entries(keywords, phr_id)

        # Convert the entries to base64 format to send over network
        entries_b64 = dict()
        for key, val in entries.items():
            key_b64 = base64.b64encode(key)
            val_b64 = base64.b64encode(val)
            entries_b64[key_b64] = val_b64

        # send the entries to HS
        res = requests.post(entries_url, data={'user_id': user_id_b64,
                                               'passwd': passwd_b64,
                                               'doc_id': doc_id_b64,
                                               'entries': entries_b64})

        if res == requests.codes.ok:
            print("entries submitted successfully")


def register(registration_url, user_id, passwd):
    """
    register a new user with the hospital server
    :param user_id:
    :param passwd:
    :return:
    """
    user_id_b64 = base64.b64encode(user_id.encode('utf-8'))
    passwd_b64 = base64.b64encode(passwd.encode('utf-8'))

    res = requests.post(registration_url, data={'user_id': user_id_b64,
                                                'passwd': passwd_b64})

    print(res.status_code)


def get_doc_ids(doc_ids_url, user_id, passwd):
    """
    :param doc_ids_url:
    :param user_id:
    :param passwd:
    :return:
    """
    user_id_b64 = base64.b64encode(user_id.encode('utf-8'))
    passwd_b64 = base64.b64encode(passwd.encode('utf-8'))

    res = requests.get(doc_ids_url, data={'user_id': user_id_b64,
                                          'passwd': passwd_b64})

    if res.status_code == requests.codes.ok:
        print(res.json())

if __name__ == '__main__':
    keywords = ['hello', 'this', 'is', 'a', 'demo']
    print(gen_entries(keywords, b'file1'))
