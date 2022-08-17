import base64
import json
import os
import shelve

import cbor2

import config
import keys
import util
from keys import master_key
from config import current_head_store_path
import requests
from util import hash, encrypt
import logging


def gen_entries(keywords, fid, enc_key) -> dict:
    """
    :param keywords: list
    :param fid: bytes
    :param enc_key: bytes
    :return:
    """
    secure_index = dict()
    nonce = os.urandom(12)
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

            # TODO: use authenticated encryption here
            enc_val = encrypt(key, nonce, cbor2.dumps([prev_addr, prev_key, fid,
                                                    enc_key]))
            # An entry in secure index
            secure_index[addr] = cbor2.dumps([enc_val, nonce])

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

    document_enc_key = util.hash(master_key, util.time_stamp())

    enc_data = util.encrypt_obj(
        keys.hs_public_key(),
        {
            'user_id': user_id,
            'passwd_hash': util.hash(passwd.encode('utf-8')),
            'doc_id': doc_id,
            'document_enc_key': util.encrypt_obj(keys.doc_public_key(),
                                                 document_enc_key)
        }
    )

    res = requests.post(phr_gen_url, data=enc_data)

    if res.status_code == requests.codes.ok:
        data = util.decrypt_obj(keys.private_key(), res.content)
        phr_id = data['phr_id']
        keywords = data['keywords']

        print(data)

        # generate the encrypted entries
        entries = gen_entries(keywords, phr_id, document_enc_key)

        print(entries)

        # encrypt the data to be sent
        enc_data = util.encrypt_obj(
            keys.hs_public_key(),
            {
                'user_id': user_id,
                'passwd_hash': util.hash(passwd.encode('utf-8')),
                'doc_id': doc_id,
                'entries': entries
            }
        )

        # send the entries to HS
        res = requests.post(entries_url, data=enc_data)

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
    enc_data = util.encrypt_obj(
        keys.hs_public_key(),
        {
            'sender_pub_key': keys.public_key_sz(),
            'trapdoor': gen_trapdoor(w)
        }
    )
    res = requests.post(config.search_url, data=enc_data)

    if res.status_code == requests.codes.ok:
        logging.info("search request successfull")
        fid_list = util.decrypt_obj(keys.private_key(), res.content)['fid_list']
        for fid in fid_list:
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

    enc_data_b64 = util.encrypt_obj(
        keys.hs_public_key(),
        {
            'user_id': user_id,
            'passwd_hash': util.hash(passwd.encode('utf-8')),
            'pub_key': keys.public_key_sz().decode('utf-8')
        }
    )

    res = requests.post(registration_url, data=enc_data_b64)

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
    # keywords = ['hello', 'this', 'is', 'a', 'demo']
    # print(gen_entries(keywords, b'file1'))

    # register(config.hs_registration_url, 'user1', '1234')
    # request_phr(config.phr_gen_url, config.entries_url, 'doc1',
                # 'user2', '1234')
    # search('some')

