import json
import secrets
import sys
import time
import shelve
import logging
from http import HTTPStatus

import cbor2
import requests
from cryptography.hazmat.primitives import serialization

import config
import keys
import util
from constants import TXN_NAMESPACE


def register():
    pass


def handle(path_components, raw_data):
    """
    :param path_components: list
    :param msg: dict
    :return:
    """
    if len(path_components) < 1:
        return

    if path_components[0] == "search":
        data = util.decrypt_obj(keys.server_ec_priv_key(), raw_data)
        trapdoor = data['trapdoor']
        sender_pub_key = serialization.load_pem_public_key(
            data['sender_pub_key'])

        addr_hex = TXN_NAMESPACE + trapdoor[:32].hex()
        key = trapdoor[32:]

        # Retrieve the head and decode it and then continute till end of list
        # is reached
        print(addr_hex)

        fid_list = list()
        while True:
            res = requests.get(config.state_url + addr_hex)
            if res.status_code == requests.codes.ok:
                logging.info("Fetched data from blockchain successfully")
                data = util.b64s_to_bytes(res.json()['data'])
                enc_data, iv = cbor2.loads(data)
                dec_data = util.decrypt(key, iv, enc_data)
                next_addr, next_key, fid, phr_key = cbor2.loads(dec_data)

                fid_list.append(fid)
                print('fid', fid)
                print('next_addr', next_addr)

                # stop upon reaching the end
                if next_addr == bytes(32):
                    break

                addr_hex = TXN_NAMESPACE + next_addr.hex()
                key = next_key
            elif res.status_code == requests.codes.not_found:
                logging.debug("Not Found")
                return HTTPStatus.NOT_FOUND, None
            else:
                logging.error("Failed to fetch data from blockchain " +
                              str(res.status_code))
                return HTTPStatus.INTERNAL_SERVER_ERROR, None

        return HTTPStatus.OK, util.encrypt_obj(sender_pub_key, {'fid_list':
                                                                   fid_list})
