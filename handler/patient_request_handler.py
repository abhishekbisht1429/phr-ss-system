import base64
import http
import logging
import secrets
import shelve
import sys
import time
import json
import config
from http import HTTPStatus
import requests
import blockchain_client as bc
import config
from constants import TXN_NAMESPACE

def __authenticate(user_id, passwd):
    with shelve.open(config.user_db_path) as udb:
        if user_id in udb and udb[user_id] == passwd:
            return HTTPStatus.OK, None
        else:
            return HTTPStatus.BAD_REQUEST, None


def handle(path_components, data):
    """
    :param path_components: list
    :param data: dict
    :return:
    """
    if len(path_components) < 1:
        return

    if path_components[0] == "register":
        user_id = data['user_id']
        passwd = data['passwd']

        # save the user_id and password on database
        with shelve.open(config.user_db_path) as udb:
            # TODO: implement check for existing user names (later)
            udb[user_id] = passwd

        return HTTPStatus.OK, None
    elif path_components[0] == "phr_gen":
        __authenticate(data['user_id'], data['passwd'])
        logging.info("user successfully authenticated")

        doc_id = data['doc_id']

        # TODO: Uncomment this and remove the temp fix

        # with shelve.open(config.doc_db_path) as doc_db:
        #     if doc_id not in doc_db:
        #         return http.HTTPStatus.BAD_REQUEST, None
        #
        #     doc_url = doc_db[doc_id]
        doc_url = 'http://localhost:9001/hs/phr_gen'

        res = requests.post(doc_url, json={'user_id': data['user_id'],
                                           'enc_key_b64': data['enc_key_b64']})

        if res.status_code == requests.codes.ok:
            return HTTPStatus.OK, json.dumps(res.json())
        else:
            return HTTPStatus.INTERNAL_SERVER_ERROR, None

        # res = requests.post()
        # return HTTPStatus.OK, json.dumps(
        #     {'phr_id_b64': str(base64.b64encode("phir_id".encode('utf-8'))),
        #      'keywords': ['this', 'is', 'sample']})

    elif path_components[0] == "entries":
        print(data)
        # TODO: Store the entries on blockchain by sending them to the
        #  blockchain node

        # Decode the entries and add to transaction list
        for key_b64, val_b64 in data['entries_b64'].items():
            key_hex = TXN_NAMESPACE + base64.b64decode(key_b64.encode(
                'utf-8')).hex()
            print(len(key_hex), key_hex)
            val = base64.b64decode(val_b64.encode('utf-8'))
            bc.add_transaction(key_hex, val)

        # submit transactions to blockchain validator
        res = bc.submit_transactions(config.batches_url)


        return HTTPStatus.OK, None
