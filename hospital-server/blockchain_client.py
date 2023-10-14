import datetime
import shelve
import sys
import time
from hashlib import sha512
import requests
import cbor2
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader, Batch, BatchList
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
import secrets
import random
from constants import ACTION_PHR_GEN, TXN_FAMILY_NAME, TXN_FAMILY_VERSION

_context = create_context('secp256k1')
_private_key = _context.new_random_private_key()
print(_private_key)
_signer = CryptoFactory(_context).new_signer(_private_key)

# urls = []

_txns = []


def submit_transactions(url):
    batch_header_bytes = BatchHeader(
        signer_public_key=_signer.get_public_key().as_hex(),
        transaction_ids=[txn.header_signature for txn in _txns]
    ).SerializeToString()
    signature = _signer.sign(batch_header_bytes)
    batch = Batch(
        header=batch_header_bytes,
        header_signature=signature,
        transactions=_txns,
        trace=True
    )

    batch_list_bytes = BatchList(batches=[batch]).SerializeToString()

    # print(batch_list_bytes)

    # send request
    try:
        resp = requests.post(
            url,
            headers={'Content-Type': 'application/octet-stream'},
            data=batch_list_bytes,
            timeout=30
        )
    except requests.Timeout:
        print('Timed out')
        return False, None
    send_time = time.time_ns()

    # clear the transaction list
    _txns.clear()

    if resp.ok:
        print("accepted")
        print(resp.json()['link'])
        # with shelve.open('asvn/temp/sent_batches') as f:
        #     status_resp = requests.get(resp.json()['link'])
        #     batch_id = status_resp.json()['data'][0]['id']
        #     f[batch_id] = send_time
        #     print(f[batch_id])
        return True, resp.json()['link']
    else:
        print("rejected")
        print(resp.json())
        return False, None


def add_transaction(action, inputs, outputs, obj):
    payload_bytes = cbor2.dumps([action, obj])

    txn_header_bytes = TransactionHeader(
        family_name=TXN_FAMILY_NAME,
        family_version=TXN_FAMILY_VERSION,
        inputs=inputs,
        outputs=outputs,
        signer_public_key=_signer.get_public_key().as_hex(),
        batcher_public_key=_signer.get_public_key().as_hex(),
        dependencies=[],
        payload_sha512=sha512(payload_bytes).hexdigest(),
        nonce=secrets.token_hex(16),
        # nonce=hex(random.randint(0, 2**64))
    ).SerializeToString()
    signature = _signer.sign(txn_header_bytes)
    txn = Transaction(header=txn_header_bytes,
                      header_signature=signature,
                      payload=payload_bytes)
    _txns.append(txn)


#
# class TransactionSubmitter:
#     def __init__(self):
#         self._txns = []
#
#     def submit(self, url):
#         batch_header_bytes = BatchHeader(
#             signer_public_key=signer.get_public_key().as_hex(),
#             transaction_ids=[txn.header_signature for txn in self._txns]
#         ).SerializeToString()
#         signature = signer.sign(batch_header_bytes)
#         batch = Batch(
#             header=batch_header_bytes,
#             header_signature=signature,
#             transactions=self._txns,
#             trace=True
#         )
#
#         batch_list_bytes = BatchList(batches=[batch]).SerializeToString()
#
#         # print(batch_list_bytes)
#
#         # send request
#         try:
#             resp = requests.post(
#                 url,
#                 headers={'Content-Type': 'application/octet-stream'},
#                 data=batch_list_bytes,
#                 timeout=30
#             )
#         except requests.Timeout:
#             print('Timed out')
#             return False
#         send_time = time.time_ns()
#
#         # clear the transaction list
#         self._txns.clear()
#
#         if resp.ok:
#             print("accepted")
#             print(resp.json()['link'])
#             with shelve.open('asvn/temp/sent_batches') as f:
#                 status_resp = requests.get(resp.json()['link'])
#                 batch_id = status_resp.json()['data'][0]['id']
#                 f[batch_id] = send_time
#                 print(f[batch_id])
#             return True
#         else:
#             print("rejected")
#             print(resp.json())
#             return False
#
#     def add(self, addr, data):
#         payload_bytes = cbor2.dumps([ACTION_SET, addr, data])
#
#         txn_header_bytes = TransactionHeader(
#             family_name=TXN_FAMILY_NAME,
#             family_version=TXN_FAMILY_VERSION,
#             inputs=[addr],
#             outputs=[addr],
#             signer_public_key=signer.get_public_key().as_hex(),
#             batcher_public_key=signer.get_public_key().as_hex(),
#             dependencies=[],
#             payload_sha512=sha512(payload_bytes).hexdigest(),
#             nonce=secrets.token_hex(16),
#             # nonce=hex(random.randint(0, 2**64))
#         ).SerializeToString()
#         signature = signer.sign(txn_header_bytes)
#         txn = Transaction(header=txn_header_bytes,
#                           header_signature=signature,
#                           payload=payload_bytes)
#
#         self._txns.append(txn)
#
#
# def main(n_txn, batch_size, n_nodes, submission_delay):
#     # n_txn = int(args[0])
#     # batch_size = int(args[1])
#     # n_nodes = int(args[2])
#     # submission_delay = int(args[3])
#     rem = n_txn % batch_size
#     n_full_batch = n_txn // batch_size
#
#     global urls
#     urls = ['http://localhost:' + str(8008 + i) + '/batches' for i in range(
#         n_nodes)]
#
#     txn_submitter = TransactionSubmitter()
#     submission_stats = [0 for i in range(n_nodes)]
#
#     accept_count = 0
#     reject_count = 0
#
#     start_time = datetime.datetime.now()
#     dummy_data_generator.init()
#     for i in range(n_full_batch):
#         for j in range(batch_size):
#             txn_submitter.add(*dummy_data_generator.generate())
#         node = random.randint(0, n_nodes - 1)
#         submission_stats[node] += 1
#         print("Batch ", i, datetime.datetime.now())
#         if txn_submitter.submit(urls[node]):
#             accept_count += 1
#             print(accept_count)
#         else:
#             reject_count += 1
#             print(reject_count)
#         time.sleep(submission_delay / 1000)
#
#     if rem > 0:
#         for j in range(rem):
#             txn_submitter.add(*dummy_data_generator.generate())
#         node = random.randint(0, n_nodes - 1)
#         submission_stats[node] += 1
#         if txn_submitter.submit(urls[node]):
#             accept_count += 1
#         else:
#             reject_count += 1
#
#     end_time = datetime.datetime.now()
#
#     # with open("./temp/logs/"+str(datetime.datetime.now()) + ".log", "w") as log:
#     #     for i in range(n_nodes):
#     #         log.write("Number of batches submitted to node " + str(i) + ": " +
#     #                   str(submission_stats[i]) + "\n")
#     print("Accept Count: ", accept_count)
#         # log.write("Accept Count: " + str(accept_count) + "\n")
#     print("Reject Count: ", reject_count)
#         # log.write("Reject Count: " + str(reject_count) + "\n")
#
#         # log.write("start time: " + str(start_time) + "\n")
#         # log.write("end time: " + str(end_time) + "\n")
#
#
#     return accept_count, reject_count
#

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("requires arguments - <number of transactions> <batch size> "
              "<number of nodes> <submission delay (ms)> ")
        exit()
    # main(*list(map(int, sys.argv[1:])))
