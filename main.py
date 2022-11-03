import json
import os
import pickle
import shelve
import signal
import time
import sys
from threading import Thread

import cbor2

import config
import keys
import util
from keys import master_key
import requests
from util import hash, encrypt
import logging
from util import Timer


def gen_entries(keywords, fid, enc_key, chd_path) -> dict:
    """
    :param chd_path:
    :param keywords: list
    :param fid: bytes
    :param enc_key: bytes
    :return:
    """
    # start_time = time.time_ns()
    timer = Timer('gen_entries', 'num_keywords', len(keywords))

    with timer:
        secure_index = dict()
        nonce = os.urandom(12)
        for w in keywords:
            kw = hash(master_key, w.encode(encoding='utf-8'))
            addr = hash(kw, fid, b'0')
            key = hash(kw, fid, b'1')

            # generate address and key of previous head
            with shelve.open(chd_path) as store:
                # TODO: find appropriate name replacement for prev_addr and prev_key
                if w not in store:
                    store[w] = bytes(32)
                    prev_addr = bytes(32)
                    prev_key = bytes(32)
                else:
                    prev_fid = store[w]
                    prev_addr = hash(kw, prev_fid, b'0')  # 32 bytes
                    prev_key = hash(kw, prev_fid, b'1')  # 32 bytes

                # TODO: Remove enc_key from the data below, it is a major
                #  security flaw. The EE can query the user for this key
                #  explicitly after receiving the phr ids. but if we assume
                #  EE to be trusted then it is fine.

                # TODO: Encrypt fid using enc_key before putting it here

                # TODO: generate nonce here.
                enc_val = encrypt(key, nonce, cbor2.dumps([prev_addr, prev_key, fid,
                                                           enc_key]))
                # An entry in secure index
                secure_index[addr] = cbor2.dumps([enc_val, nonce])

                # Update the current head store
                store[w] = fid
        # end_time = time.time_ns()
        # duration = (end_time - start_time) / 1e6
        # logging.info("Generate Entries Duration: {} ms".format(duration))
        return secure_index


def request_phr(phr_gen_url, entries_url, doc_id, user_id, passwd, chd_path):
    """
    Request generation of PHR from doctor
    :return:
    """
    # convert the user_id and password into base64 encoding to send over the
    # network
    timer = Timer('request_phr', user_id, doc_id)

    # start_time = time.time_ns()
    with timer:
        document_enc_key = util.hash(master_key, util.time_stamp())
        # TODO: create a store to store doc enc key

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

            # print(data)

            # generate the encrypted entries
            entries = gen_entries(keywords, phr_id, document_enc_key, chd_path)

            # print(entries)

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

            if res.status_code == requests.codes.ok:
                logging.debug("entries submitted successfully")
                # end_time = time.time_ns()
                # duration = (end_time - start_time) / 1e6
                # logging.info("PHR Generation Duration: {} ms".format(duration))
                return True
        return False


def gen_trapdoor(w, chd_path):
    timer = Timer('gen_trapdoor', w)
    # start_time = time.time_ns()
    with timer:
        kw = hash(master_key, w.encode(encoding='utf-8'))
        with shelve.open(chd_path) as store:
            if w not in store:
                logging.debug("No such keyword found in store")
                prev_fid = bytes(32)
            else:
                prev_fid = store[w]

            addr = hash(kw, prev_fid, b'0')
            key = hash(kw, prev_fid, b'1')

            # end_time = time.time_ns()
            # duration = (end_time - start_time)/1e6
            # print("Trapdoor Generation Time: {} ms".format(duration))
            return addr + key


def search(w, user_name):
    timer = Timer('search', w, user_name)
    # start_time = time.time_ns()
    with timer:
        chd_path = config.current_head_store_path + '_' + user_name
        enc_data = util.encrypt_obj(
            keys.hs_public_key(),
            {
                'sender_pub_key': keys.public_key_sz(),
                'trapdoor': gen_trapdoor(w, chd_path)
            }
        )
        res = requests.post(config.search_url, data=enc_data)

        if res.status_code == requests.codes.ok:
            logging.debug("search request successfull")
            fid_list = util.decrypt_obj(keys.private_key(), res.content)['fid_list']
            # end_time = time.time_ns()
            # duration = (end_time - start_time) / 1e6
            # print("Search Time Duration: {} ms".format(duration))
            for fid in fid_list:
                print(fid)
            return fid_list
        else:
            logging.error("search request failed, status code " +
                          str(res.status_code))
            return None


def register(registration_url, user_id, passwd):
    """
    register a new user with the hospital server
    :param user_id:
    :param passwd:
    :return:
    """
    # user_id_b64 = base64.b64encode(user_id.encode('utf-8'))
    # passwd_b64 = base64.b64encode(passwd.encode('utf-8'))
    timer = Timer('register', user_id)
    with timer:
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
            return True
        return False


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


def sigint_handler(signum, frame):
    util.Timer.stop_sync()


signal.signal(signal.SIGINT, sigint_handler)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
    # keywords = ['hello', 'this', 'is', 'a', 'demo']
    # print(gen_entries(keywords, b'file1'))

    # NOTE: Delete current_head for a fresh start
    # register(config.hs_registration_url, 'user1', '1234')
    # request_phr(config.phr_gen_url, config.entries_url, 'doc1',
    #             'user1', '1234')
    # search('some')

    # start timer thread
    timer_thread = Thread(target=util.Timer.bg_sync)
    timer_thread.start()

    while True:
        print("=========================================================")
        print("1. Register")
        print("2. Request PHR")
        print("3. Search")
        print("4. Exit")
        choice = int(input('Choice: '))
        if choice == 1:
            user_name = input("User Name: ")
            password = input("Password: ")
            # Delete current_head for a fresh start
            if os.path.exists(config.current_head_store_path + '_' + user_name):
                os.remove(config.current_head_store_path + '_' + user_name)
            if register(config.hs_registration_url, user_name, password):
                print("Registration Successful")
            else:
                print("Error during registration")
        elif choice == 2:
            user_name = input("User Name: ")
            password = input("Password: ")
            doc_id = input("Doctor ID: ")
            if request_phr(config.phr_gen_url, config.entries_url, doc_id,
                           user_name, password,
                           config.current_head_store_path + '_' + user_name):
                print("PHR Generated Successfully")
            else:
                print("Failed to Generate PHR")
        elif choice == 3:
            user_name = input('User Name: ')
            keyword = input("Keyword: ")
            fid_list = search(keyword,
                              user_name)
            print('fid list: ', fid_list)
            pass
        elif choice == 4:
            break
        else:
            print("Invalid Choice.")

        print(Timer._store)
        # with open('temp/timer_db', 'wb') as timer_db:
        #     timer_db.write(pickle.dumps(util.Timer.store))
        # Timer.save()
    logging.info("Exiting")
    timer_thread.join()
# PHR database
# Graphs and simulation results
