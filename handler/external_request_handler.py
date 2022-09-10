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
from constants import TXN_NAMESPACE, ACTION_SEARCH
import blockchain_client as bc
import blockchain_event_listener as bel
from threading import Thread

# search_event_listener = bel.SearchEventListener(config.validator_url)
# event_thread = Thread(target=search_event_listener.listen)
# event_thread.start()


def register():
    pass


def handle(path_components, raw_data, search_event_listener):
    """
    :param path_components: list
    :param msg: dict
    :return:
    """
    if len(path_components) < 1:
        return

    if path_components[0] == "search":
        enc_fid_list = util.decrypt_obj(keys.server_ec_priv_key(), raw_data)
        trapdoor = enc_fid_list['trapdoor']
        sender_pub_key_sz = enc_fid_list['sender_pub_key']

        addr_hex = TXN_NAMESPACE + trapdoor[:32].hex()
        out_addr_hex = keys.serialized_pub_key()[:32].hex()
        key = trapdoor[32:]

        # Retrieve the head and decode it and then continute till end of list
        # is reached
        print(addr_hex)

        # TODO: Encrypt and send this trapdoor
        request_id = util.time_stamp().hex()
        bc.add_transaction(
            action=ACTION_SEARCH,
            inputs=[TXN_NAMESPACE],
            outputs=[TXN_NAMESPACE],
            data=(
                util.bytes_to_b64s(trapdoor),
                util.bytes_to_b64s(sender_pub_key_sz),
                request_id
            )
        )
        # subscribe to event first and then send the transaction
        if bc.submit_transactions(config.batches_url):
            # wait till status is committed
            enc_fid_list = search_event_listener.wait_for_event(request_id)
            if enc_fid_list is None:
                logging.error("Search event not received")
                return HTTPStatus.REQUEST_TIMEOUT, None
            return HTTPStatus.OK, enc_fid_list
        else:
            logging.error("Transaction submission timed out")
            return HTTPStatus.REQUEST_TIMEOUT, None

        # fid_list = list()
        # while True:
        #     res = requests.get(config.state_url + addr_hex)
        #     if res.status_code == requests.codes.ok:
        #         logging.info("Fetched data from blockchain successfully")
        #         data = util.b64s_to_bytes(res.json()['data'])
        #         enc_data, iv = cbor2.loads(data)
        #         dec_data = util.decrypt(key, iv, enc_data)
        #         next_addr, next_key, fid, phr_key = cbor2.loads(dec_data)
        #
        #         fid_list.append(fid)
        #         print('fid', fid)
        #         print('next_addr', next_addr)
        #
        #         # stop upon reaching the end
        #         if next_addr == bytes(32):
        #             break
        #
        #         addr_hex = TXN_NAMESPACE + next_addr.hex()
        #         key = next_key
        #     elif res.status_code == requests.codes.not_found:
        #         logging.debug("Not Found")
        #         return HTTPStatus.NOT_FOUND, None
        #     else:
        #         logging.error("Failed to fetch data from blockchain " +
        #                       str(res.status_code))
        #         return HTTPStatus.INTERNAL_SERVER_ERROR, None
        #
        # return HTTPStatus.OK, util.encrypt_obj(sender_pub_key, {'fid_list':
        #                                                             fid_list})
