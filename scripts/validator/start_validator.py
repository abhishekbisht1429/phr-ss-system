# This script will be run by the validator container
import http
import os
import queue
import sys
import threading
import time
import requests
import toml

import config
import logging
import util
import socketserver
from threading import Thread
import socket
import pickle
import subprocess
import json


# find a way to use node_info_list

class NotificationReceiver:
    class TCPHandler(socketserver.StreamRequestHandler):
        data_queue = queue.Queue()
        cv = threading.Condition()

        def handle(self) -> None:
            logging.debug("handling request from" + str(self.client_address))
            # if self.client_address[0] == config.kds_ip:
            data_len = int.from_bytes(self.rfile.read(4),
                                      byteorder='big')
            logging.debug("data_len: " + str(data_len))
            with self.cv:
                self.data_queue.put(pickle.loads(self.rfile.read(data_len)))
                # notify the main thread if it is waiting
                logging.debug("Notifying the main Thread")
                self.cv.notify()
            # else:
            #     self.wfile.close()

    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self._tcp_server = socketserver.TCPServer(
            (ip, port),
            NotificationReceiver.TCPHandler,
            bind_and_activate=False
        )
        self._lock = threading.Lock()
        self._is_running = False

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def start(self):
        with self._lock:
            if self._is_running:
                raise Exception("Server already running")
            logging.info("Starting server at " + str(self._ip) + ':' + str(
                self._port))

            def f(notif_server):
                with notif_server._tcp_server:
                    while notif_server._is_running:
                        notif_server._tcp_server.handle_request()
                        logging.debug("Request Handled")

            self._tcp_server.server_bind()
            self._tcp_server.server_activate()
            self._is_running = True
            threading.Thread(target=f, args=(self,)).start()
            logging.info("Server started")

    def stop(self):
        logging.debug("stop called")
        with self._lock:
            if not self._is_running:
                raise Exception("Server is not running")
            logging.debug("Shutting down server")
            self._is_running = False
            try:
                socket.create_connection((self._ip, self._port)).close()
            except Exception as e:
                # server already closed
                logging.debug(str(e))
            logging.info("Server stopped")
            self._tcp_server.server_close()

    def get_data(self):
        # acquire the lock
        with self.TCPHandler.cv:
            # consume the data
            if self.TCPHandler.data_queue.empty():
                logging.debug("main thread waiting")
                self.TCPHandler.cv.wait()
            return self.TCPHandler.data_queue.get()

    def is_running(self):
        with self._lock:
            return self._is_running


def generate_keys():
    # generate user keys
    if not os.path.exists(config.user_key_dir):
        os.makedirs(config.user_key_dir)
    user_keygen_cmd = ["sawtooth", "keygen", "--key-dir", config.user_key_dir]
    if subprocess.run(user_keygen_cmd).returncode != 0:
        logging.error("Failed to generate user keys")
        exit(1)

    # generate validator keys
    # NOTE: the sawadm keygen command does not give an option to specify
    # directory where keys should be created
    validator_keygen_cmd = ["sawadm", "keygen", "--force"]
    if subprocess.run(validator_keygen_cmd).returncode != 0:
        logging.error("Failed to generate validator keys")
        exit(1)

    logging.info("Generated keys")


def create_genesis_block(node_info_list):
    user_sk_path = os.path.join(config.user_key_dir, 'root.priv')

    # generate genesis settings file
    genesis_settings_file = 'config-genesis.batch'
    genesis_settings_cmd = ['sawset', 'genesis',
                            '--key', user_sk_path,
                            '-o', genesis_settings_file]
    if subprocess.run(genesis_settings_cmd).returncode != 0:
        logging.error("Falied to create genesis settings file")
        exit(1)

    # create settings proposal for genesis block
    genesis_proposal_file = 'config-consensus.batch'
    member_keys = list()
    for node_info in node_info_list:
        member_keys.append(node_info['pk'])
    member_keys_json = json.dumps(member_keys)
    settings_proposal_cmd = [
        'sawset', 'proposal', 'create',
        '--key', user_sk_path,
        '-o', genesis_proposal_file,
        'sawtooth.consensus.algorithm.name=pbft',
        'sawtooth.consensus.algorithm.version=1.0',
        'sawtooth.consensus.pbft.members=' + member_keys_json,
        'sawtooth.consensus.pbft.block_publishing_delay=0'
    ]
    if subprocess.run(settings_proposal_cmd).returncode != 0:
        logging.error("Falied to create settings proposal for genesis block")
        exit(1)

    # create genesis block
    genesis_block_cmd = ['sawadm', 'genesis',
                         genesis_settings_file, genesis_proposal_file]
    if subprocess.run(genesis_block_cmd).returncode != 0:
        logging.error("Failed to create genesis block")
        exit(1)


def generate_validator_config(network_port,
                              component_port,
                              consensus_port, node_info_list, node_id,
                              gateway_ip):
    validator_config = dict()
    network_endpoint = 'network:tcp://eth0:' + str(network_port)
    component_endpoint = 'component:tcp://eth0:' + str(component_port)
    consensus_endpoint = 'consensus:tcp://eth0:' + str(consensus_port)
    validator_config['bind'] = [
        network_endpoint,
        component_endpoint,
        consensus_endpoint
    ]
    peer_list = list()
    for i in range(0, node_id):
        node_info = node_info_list[i]
        peer_list.append(
            'tcp://' + node_info['gateway_ip'] + ':'
            + str(node_info['validator_port'])
        )
    logging.debug('peer list: ' + str(peer_list))

    validator_config['endpoint'] = 'tcp://' + gateway_ip + ':' \
                                   + str(network_port)
    validator_config['peering'] = 'static'
    validator_config['peers'] = peer_list
    validator_config['scheduler'] = 'parallel'
    validator_config['network_public_key'] = config.network_pk
    validator_config['network_private_key'] = config.network_sk
    validator_config['minimum_peer_connectivity'] = 3
    validator_config['maximum_peer_connectivity'] = 100

    with open(config.validator_config_file, 'w') as config_file:
        toml.dump(validator_config, config_file)
    logging.info('Generated validator.toml')


def start_validator(network_port, component_port,
                    consensus_port,
                    node_info_list, node_id, gateway_ip):
    logging.debug("Trying to start validator with node id="+str(node_id))
    if node_id == 0:
        create_genesis_block(node_info_list)
    generate_validator_config(network_port,
                              component_port,
                              consensus_port, node_info_list, node_id,
                              gateway_ip)

    logging.info("Starting sawtooth validator")
    if subprocess.run(['sawtooth-validator', '-vvv']) != 0:
        logging.error("Falied to start validator")
        exit(1)


def main(args):
    validator_container_name = args[0]
    gateway_ip = args[1]
    network_port = int(args[2])
    component_port = int(args[3])
    consensus_port = int(args[4])
    notif_receiver_port = int(args[5])

    logging.basicConfig(level=logging.DEBUG)

    # Prepare the notification receiver
    notif_receiver = \
        NotificationReceiver(validator_container_name, notif_receiver_port)
    with notif_receiver:
        generate_keys()

        # retrieve the public key
        validator_pk_path = os.path.join(config.validator_key_dir,
                                         'validator.pub')
        with open(validator_pk_path) as pk_file:
            pk = pk_file.read().strip()
        logging.info("Validator Public Key: " + pk)

        # send the public key generated by sawadm keygen to kds along with
        # gateway_ip and forwarded port
        logging.info("Sending request to kds")
        logging.debug('notif receiver port: ' + str(notif_receiver_port))
        logging.debug('network port: ' + str(network_port))
        resp = requests.post(config.kds_url, data=util.serialize_obj({
            'pk': pk,
            'gateway_ip': gateway_ip,
            'validator_port': network_port,
            'notif_receiver_port': notif_receiver_port
        }), timeout=4)

        if resp.status_code != http.HTTPStatus.OK:
            logging.error("request sent to KDS failed ", resp.status_code)
            exit(1)

        logging.info("Waiting for KDS to send data...")
        data = notif_receiver.get_data()
        logging.debug("Wait over")

        node_info_list = data['node_info_list']
        node_id = data['id']
        logging.debug("node_info_list: " + str(node_info_list))

    # start the validator
    start_validator(network_port, component_port,
                    consensus_port, node_info_list, node_id, gateway_ip)


if __name__ == '__main__':
    if len(sys.argv) < 7:
        print('required - <validator container name> <gateway ip> '
              '<network_port> '
              '<component_port> <consensus_port> <notif_receiver_port>')
        exit(1)
    main(sys.argv[1:])
