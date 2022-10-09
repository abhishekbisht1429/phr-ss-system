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
            while len(node_info_list) < config.total_nodes:
                cv.wait()

            # send the node info list to all the nodes
            data = pickle.dumps(node_info_list)
            data_len = len(data)
            for node_info in node_info_list:
                logging.debug('node info ' + str(node_info))
                sock = socket.create_connection((node_info['ip'], node_info[
                    'port']))
                sock.send(data_len.to_bytes(4, byteorder='big'))
                sock.send(data)
                sock.close()
            node_info_list.clear()

    # send the node info list to all the nodes
monitor_thread = Thread(target=monitor_list)
monitor_thread.start()

def handle(path_components, raw_data):
    """
    :param path_components: list
    :param msg: dict
    :return:
    """
    if len(path_components) < 1:
        return HTTPStatus.NOT_FOUND, None

    if path_components[0] == "submit":
        data = util.deserialize_obj(raw_data)
        if type(data) is dict and 'ip' in data and 'port' in data and 'pk' in\
                data:
            with cv:
                node_info_list.append(data)
                cv.notify()
            return HTTPStatus.OK, None
        else:
            return HTTPStatus.UNPROCESSABLE_ENTITY, None
    else:
        return HTTPStatus.NOT_FOUND, None
