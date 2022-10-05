import sys

import cbor2
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_sdk.processor.handler import TransactionHandler

from transaction_family import TransactionPayload, State, InvalidAction, \
    NAMESPACE, NAME, VERSION, EVENT_SEARCH_COMPLETE

import logging

from constants import ACTION_SET, ACTION_DEL, ACTION_SEARCH
import util

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def search(state, trapdoor, ee_pub_key_sz, request_id):
    addr = NAMESPACE + trapdoor[:32].hex()
    key = trapdoor[32:]
    fid_list = list()
    while True:
        state_entry = state.get(addr)
        if state_entry is None:
            break
        enc_data, nonce = cbor2.loads(state_entry.data)
        dec_data = util.decrypt(key, nonce, enc_data)
        next_addr, next_key, fid, phr_key = cbor2.loads(dec_data)

        fid_list.append(fid)
        logging.error('fid {}'.format(str(fid)))
        logging.error('next_addr {}'.format(next_addr))

        if next_addr == bytes(32):
            break

        addr = NAMESPACE + next_addr.hex()
        key = next_key
    print('Outside while loop')
    logging.error("Outside while loop")
    ee_pub_key = serialization.load_pem_public_key(ee_pub_key_sz)
    enc_fid_list = util.encrypt_obj(ee_pub_key, {'fid_list': fid_list})
    # state.set(res_addr, enc_fid_list)
    state.add_event(
        event_type=EVENT_SEARCH_COMPLETE,
        attributes=[('id', request_id)],
        data=enc_fid_list
    )
    logging.error('added event')
    print('added event')


class CustomTransactionHandler(TransactionHandler):

    @property
    def family_name(self):
        return NAME

    @property
    def family_versions(self):
        return [VERSION]

    @property
    def namespaces(self):
        return [NAMESPACE]

    # The argument transaction is an instance of the class Transaction that
    # is created from the protobuf definition. Also, context is an instance of
    # the class Context from the python SDK.
    def apply(self, transaction, context):
        logger.error("inside apply")
        header = transaction.header
        signer = header.signer_public_key

        # print(transaction.payload)

        transaction = TransactionPayload.from_bytes(transaction.payload)
        state = State(context)
        logger.error(transaction.data)
        logger.error(self.namespaces)

        if transaction.action == ACTION_SET:
            addr = transaction.data[0]
            logging.info(addr)
            value = transaction.data[1]
            state.set(addr, value)
        elif transaction.action == ACTION_DEL:
            addr = transaction.data
        elif transaction.action == ACTION_SEARCH:
            data = transaction.data
            logging.info(data)
            trapdoor = util.b64s_to_bytes(data[0])
            hs_pub_key_sz = util.b64s_to_bytes(data[1])
            request_id = data[2]
            search(state, trapdoor, hs_pub_key_sz, request_id)
            # addr = util.b64s_to_bytes(data[0])
            # pub_key_serialized = util.b64s_to_bytes(data[1])
            # print(addr)
            # print(pub_key_serialized)
        else:
            raise InvalidAction(transaction.action)


def main(url):
    # tcp://localhost:4004
    processor = TransactionProcessor(url=url)
    processor.add_handler(CustomTransactionHandler())
    processor.start()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("invalid number of args")
        exit(1)
    main(sys.argv[1])
