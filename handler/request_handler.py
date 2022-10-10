import logging
import threading
from http import HTTPStatus
import util
import config
from threading import Thread
import socket
import pickle

node_info_list = list()
cv = threading.Condition()

def monitor_list():
    while True:
        with cv:
            # wait till required number of node_info have arrived
            cv.wait()

            # send the node info list to all the nodes
            for i, node_info in enumerate(node_info_list):
                logging.debug('node info ' + str(node_info))
                sock = socket.create_connection(
                    (node_info['gateway_ip'], node_info['notif_receiver_port'])
                )
                data = pickle.dumps({'id': i,
                        'node_info_list': node_info_list})
                data_len = len(data)
                sock.send(data_len.to_bytes(4, byteorder='big'))
                sock.send(data)
                sock.close()
            node_info_list.clear()

    # send the node info list to all the nodes
monitor_thread = Thread(target=monitor_list)
monitor_thread.start()

def handle(client_address, path_components, raw_data):
    """
    :param path_components: list
    :param msg: dict
    :return:
    """
    if len(path_components) < 1:
        return HTTPStatus.NOT_FOUND, None

    if path_components[0] == "submit":
        data = util.deserialize_obj(raw_data)
        with cv:
            node_info_list.append({
                'gateway_ip': data['gateway_ip'],
                'validator_port': data['validator_port'],
                'pk': data['pk'],
                'notif_receiver_port': data['notif_receiver_port']
            })
            if len(node_info_list) == config.total_nodes:
                cv.notify()
        return HTTPStatus.OK, None
    else:
        return HTTPStatus.NOT_FOUND, None
