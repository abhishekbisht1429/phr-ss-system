import sys

import cbor2
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_sdk.processor.handler import TransactionHandler

from transaction_family import TransactionPayload, State, InvalidAction, \
    NAMESPACE, NAME, VERSION, EVENT_SEARCH_COMPLETE, EVENT_PHR_GEN

import logging

from transaction_family import ACTION_PHR_GEN, ACTION_DEL, ACTION_SEARCH
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
        logging.debug('fid {}'.format(str(fid)))
        logging.debug('next_addr {}'.format(next_addr))

        if next_addr == bytes(32):
            break

        addr = NAMESPACE + next_addr.hex()
        key = next_key
    logging.debug('Outside while loop')
    ee_pub_key = serialization.load_pem_public_key(ee_pub_key_sz)
    enc_fid_list = util.encrypt_obj(ee_pub_key, {'fid_list': fid_list})
    # state.set(res_addr, enc_fid_list)
    state.add_event(
        event_type=EVENT_SEARCH_COMPLETE,
        attributes=[('id', request_id)],
        data=enc_fid_list
    )
    logging.info('added event')
    # print('added event')


def phr_gen_v1(transaction, state):
    request_id = transaction.data[0]
    secure_entries = transaction.data[1]
    for addr, value in secure_entries.items():
        addr_hex = NAMESPACE + addr.hex()
        logging.debug('address: {}'.format(addr_hex))
        state.set(addr_hex, value)
    state.add_event(
        event_type=EVENT_PHR_GEN,
        attributes=[('id', request_id)]
    )


def phr_gen_v2(transaction, state):
    addr_hex = transaction.data[0]
    val = transaction.data[1]
    state.set(addr_hex, val)
    logging.debug('State set at {} '.format(addr_hex))
    state.add_event(
        event_type=EVENT_PHR_GEN,
        attributes=[('id', addr_hex)]
    )


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
        logger.debug("inside apply")
        header = transaction.header
        signer = header.signer_public_key

        # print(transaction.payload)

        transaction = TransactionPayload.from_bytes(transaction.payload)
        state = State(context)
        logger.debug(transaction.data)
        logger.debug(self.namespaces)

        if transaction.action == ACTION_PHR_GEN:
            if transaction.data[2] == 'v1':
                phr_gen_v1(transaction, state)
            elif transaction.data[2] == 'v2':
                phr_gen_v2(transaction, state)
        elif transaction.action == ACTION_DEL:
            addr = transaction.data
        elif transaction.action == ACTION_SEARCH:
            data = transaction.data
            logging.debug(data)
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


def main(url, verbose_level=0):
    # tcp://localhost:4004

    # TODO: set the log levels properly
    if verbose_level == 0:
        logging.basicConfig(level=logging.NOTSET)
    if verbose_level == 1:
        logging.basicConfig(level=logging.ERROR)
    elif verbose_level == 2:
        logging.basicConfig(level=logging.WARN)
    elif verbose_level == 3:
        logging.basicConfig(level=logging.INFO)
    elif verbose_level == 4:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    processor = TransactionProcessor(url=url)
    processor.add_handler(CustomTransactionHandler())
    processor.start()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("invalid number of args")
        exit(1)
    if len(sys.argv) < 3:
        main(sys.argv[1])
    else:
        main(sys.argv[1], verbose_level=int(sys.argv[2]))
