import base64
import json
import os
import shelve

import cbor2

import config
import util
from client_keys import master_key
from config import current_head_store_path
import requests
from util import hash, encrypt
import logging


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
                store[w] = bytes(32)
                prev_addr = bytes(32)
                prev_key = bytes(32)
            else:
                prev_fid = store[w]
                prev_addr = hash(kw, prev_fid, b'0') # 32 bytes
                prev_key = hash(kw, prev_fid, b'1') # 32 bytes

            # enc_val = encrypt(key, iv, prev_addr + prev_key + fid + iv)
            enc_val = encrypt(key, iv, cbor2.dumps([prev_addr, prev_key, fid]))
            # An entry in secure index
            secure_index[addr] = cbor2.dumps([enc_val, iv])

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

    # TODO: encrypt enc_key using public key of doctor
    enc_key = util.hash(master_key, util.time_stamp())
    enc_key_b64 = base64.b64encode(enc_key).decode('utf-8')
    res = requests.post(phr_gen_url, json={'user_id': user_id,
                                           'passwd': passwd,
                                           'doc_id': doc_id,
                                           'enc_key_b64': enc_key_b64})

    if res.status_code == requests.codes.ok:
        data = res.json()
        phr_id = base64.b64decode(data['phr_id_b64'].encode('utf-8'))
        keywords = data['keywords']

        print(data)

        # generate the encrypted entries
        entries = gen_entries(keywords, phr_id)

        print(entries)
        # Convert the entries to base64 format to send over network
        entries_b64 = dict()
        for key, val in entries.items():
            key_b64 = base64.b64encode(key).decode('utf-8')
            val_b64 = base64.b64encode(val).decode('utf-8')
            entries_b64[key_b64] = val_b64

        # send the entries to HS
        res = requests.post(entries_url, json={'user_id': user_id,
                                               'passwd': passwd,
                                               'doc_id': doc_id,
                                               'entries_b64': entries_b64})

        if res == requests.codes.ok:
            print("entries submitted successfully")

def gen_trapdoor(w):
    kw = hash(master_key, w.encode(encoding='utf-8'))
    with shelve.open(current_head_store_path) as store:
        if w not in store:
            logging.debug("No such keyword found in store")
            prev_fid = bytes(32)
        else:
            prev_fid = store[w]

        addr = hash(kw, prev_fid, b'0')
        key = hash(kw, prev_fid, b'1')

        return addr + key


def search(w):
    trapdoor_b64 = util.bytes_to_base64(gen_trapdoor(w))
    res = requests.post(config.search_url, json={'trapdoor_b64': trapdoor_b64})

    if res.status_code == requests.codes.ok:
        logging.info("search request successfull")
        fid_list = res.json()['fid_list']
        for fid_b64 in fid_list:
            fid = util.b64_to_bytes(fid_b64)
            print(fid)
    else:
        logging.error("search request failed, status code " +
                      str(res.status_code))

def register(registration_url, user_id, passwd):
    """
    register a new user with the hospital server
    :param user_id:
    :param passwd:
    :return:
    """
    # user_id_b64 = base64.b64encode(user_id.encode('utf-8'))
    # passwd_b64 = base64.b64encode(passwd.encode('utf-8'))

    res = requests.post(registration_url, json={'user_id': user_id,
                                                'passwd': passwd})

    if res.status_code == requests.codes.ok:
        logging.info('Registration Successful')


def get_doc_ids(doc_ids_url, user_id, passwd):
    """
    :param doc_ids_url:
    :param user_id:
    :param passwd:
    :return:
    """

    res = requests.get(doc_ids_url, data=json.dumps({'user_id': user_id,
                                                     'passwd': passwd}))

    if res.status_code == requests.codes.ok:
        print(res.json())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    keywords = ['hello', 'this', 'is', 'a', 'demo']
    # print(gen_entries(keywords, b'file1'))

    # register(config.hs_registration_url, 'abhishek', 'bisht')
    # request_phr(config.phr_gen_url, config.entries_url, 'doctor1',
    #             'abhishek', 'bisht')
    search('some')

