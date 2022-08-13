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
from constants import TXN_NAMESPACE

def __authenticated(user_id, passwd_hash):
    with shelve.open(config.user_db_path) as udb:
        if user_id in udb and udb[user_id][1] == passwd_hash:
            return serialization.load_pem_public_key(udb[user_id][0])


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
        user_pub_key = __authenticated(data['user_id'], data['passwd_hash'])
        if not user_pub_key:
            return HTTPStatus.BAD_REQUEST, None

        logging.info("user ")

        doc_id = data['doc_id']

        # TODO: Uncomment the lines below and remove the temp fix
        # with shelve.open(config.doc_db_path) as doc_db:
        #     if doc_id not in doc_db:
        #         return http.HTTPStatus.BAD_REQUEST, None
        #
        #     doc_url = doc_db[doc_id]
        doc_url = 'http://localhost:9001/hs/phr_gen'

        res = requests.post(doc_url, json={
            'user_id': data['user_id'],
            'enc_key_b64': util.bytes_to_b64s(data['document_enc_key'])
        })

        enc_res = util.encrypt_obj(user_pub_key, res.json())
        if res.status_code == requests.codes.ok:
            return HTTPStatus.OK, enc_res
        else:
            return HTTPStatus.INTERNAL_SERVER_ERROR, None


    elif path_components[0] == "entries":
        data = util.decrypt_obj(keys.server_ec_priv_key(), raw_data)
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
            bc.add_transaction(key_hex, val)

        # submit transactions to blockchain validator
        res = bc.submit_transactions(config.batches_url)

        return HTTPStatus.OK, None
