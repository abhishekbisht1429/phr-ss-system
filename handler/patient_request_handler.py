import base64
import http
import logging
import secrets
import shelve
import sys
import time
import json

import cbor2
from cryptography.hazmat.primitives import serialization

import config
from http import HTTPStatus
import requests
import blockchain_client as bc
import config
import keys
import util
from constants import TXN_NAMESPACE, ACTION_SET


def __authenticated(user_id, passwd_hash):
    with shelve.open(config.user_db_path) as udb:
        if user_id in udb and udb[user_id][1] == passwd_hash:
            return udb[user_id][0]


def __decrypt(enc_data):
    return cbor2.loads(
        util.ecies_decryption(
            keys.server_ec_priv_key(),
            base64.b64decode(enc_data)
        )
    )

def handle(path_components, raw_data):
    """
    :param path_components: list
    :param data: dict
    :return:
    """
    if len(path_components) < 1:
        return

    if path_components[0] == "register":
        with util.Timer('register'):
            data = util.decrypt_obj(keys.server_ec_priv_key(), raw_data)
            user_id = data['user_id']
            passwd_hash = data['passwd_hash']
            pub_key = data['pub_key'].encode('utf-8')

            # save the user_id and password on database
            with shelve.open(config.user_db_path) as udb:
                # TODO: implement check for existing user names (later)
                udb[user_id] = (pub_key, passwd_hash)

            return HTTPStatus.OK, None
    elif path_components[0] == "phr_gen":
        data = util.decrypt_obj(keys.server_ec_priv_key(), raw_data)
        with util.Timer('phr_gen', data['user_id']):
            user_pub_key_sz = __authenticated(data['user_id'],
                                              data['passwd_hash'])
            user_pub_key = serialization.load_pem_public_key(user_pub_key_sz)
            if not user_pub_key:
                return HTTPStatus.BAD_REQUEST, None

            logging.info("user ")

            doc_id = data['doc_id']

            with shelve.open(config.doc_db_path) as doc_db:
                if doc_id not in doc_db:
                    return http.HTTPStatus.BAD_REQUEST, None
                doc_url = doc_db[doc_id]['url'] + '/' + config.phr_gen_seg
                doc_pub_key = serialization.load_pem_public_key(doc_db[doc_id][
                                                                    'pub_key'])
            print(doc_url)

            res = requests.post(doc_url, data=util.encrypt_obj(doc_pub_key, {
                'user_id': data['user_id'],
                'user_pub_key': user_pub_key_sz,
                'doc_enc_key': data['document_enc_key']
            }))

            # enc_res = util.encrypt_obj(user_pub_key, res.json())
            if res.status_code == requests.codes.ok:
                return HTTPStatus.OK, res.content
            else:
                return HTTPStatus.INTERNAL_SERVER_ERROR, None


    elif path_components[0] == "entries":
        data = util.decrypt_obj(keys.server_ec_priv_key(), raw_data)
        with util.Timer('entries', data['user_id']):
            user_pub_key = __authenticated(data['user_id'], data['passwd_hash'])
            if not user_pub_key:
                return HTTPStatus.BAD_REQUEST, None
            print(data)
            # TODO: Store the entries on blockchain by sending them to the
            #  blockchain node

            # Decode the entries and add to transaction list
            for key, val in data['entries'].items():
                key_hex = TXN_NAMESPACE + key.hex()
                print(len(key_hex), key_hex)
                bc.add_transaction(action=ACTION_SET,
                                   inputs=[TXN_NAMESPACE],
                                   outputs=[TXN_NAMESPACE],
                                   data=(key_hex, val))

            # submit transactions to blockchain validator
            accepted, info = bc.submit_transactions(config.batches_url)

            if accepted:
                return HTTPStatus.OK, None
            else:
                return HTTPStatus.INTERNAL_SERVER_ERROR, None
