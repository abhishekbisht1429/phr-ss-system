import sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from threading import Thread
import pickle
import config
import os.path
import urllib.parse as parse
import threading
import logging
import socket
import signal

from handler import bn_request_handler, ipfs_request_handler

node_info_list = list()
continue_distribution = True
distribution_condition = threading.Condition()


def distribute_info():
    while continue_distribution:
        with distribution_condition:
            # wait till required number of node_info have arrived
            distribution_condition.wait()

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
    logging.info("Distribution Thread exiting")


class HSRequestHandler(BaseHTTPRequestHandler):

    def respond(self, res_code, data):
        # return response to the server
        if res_code is not None:
            self.send_response(res_code, self.responses[res_code][0])
            self.end_headers()
            if data is not None:
                self.wfile.write(data)
        else:
            self.send_error(404)
            self.end_headers()

    def do_POST(self):
        # Split path into its components
        path = parse.urlparse(self.path).path
        path_components = path.split(os.path.sep)
        # print("get: ", path_components)

        # check if appropriate number of parameters have been provided
        if len(path_components) < 2:
            self.send_error(404)
            self.end_headers()
            return

        # headers
        # print(self.headers.keys())
        content_len = self.headers.get('Content-Length')
        if content_len is None:
            self.send_error(411)
            self.end_headers()
            return
        content_len = int(content_len)
        # delegate the task to appropriate handler

        data = None
        if content_len > 0:
            data = self.rfile.read(content_len)

        # Send the request to appropriate handler
        logging.info("received request from : " + str(self.client_address))
        if path_components[1] == "blockchain":
            res_code, data = bn_request_handler.handle(
                path_components[2:],
                data,
                node_info_list,
                distribution_condition
            )
        elif path_components[1] == "ifps":
            res_code, data = ipfs_request_handler.handle_post(
                path_components[2:],
                data
            )
        else:
            res_code, data = None, None

        self.respond(res_code, data)

    def do_GET(self):
        # Split path into its components
        path = parse.urlparse(self.path).path
        path_components = path.split(os.path.sep)
        # print("get: ", path_components)

        # check if appropriate number of parameters have been provided
        if len(path_components) < 2:
            self.send_error(404)
            self.end_headers()
            return

        # Send the request to appropriate handler
        logging.info("received request from : " + str(self.client_address))
        if path_components[1] == "ipfs":
            logging.debug("delegating request to ipfs request handler")
            res_code, data = ipfs_request_handler.handle_get(
                path_components[2:],
                self.headers
            )
        else:
            res_code, data = None, None

        self.respond(res_code, data)


def sigint_handler(signum, frame):
    logging.info("Stopping distribution thread")
    with distribution_condition:
        global continue_distribution
        continue_distribution = False
        distribution_condition.notify_all()

    logging.info("Shutting Down Server")
    server.shutdown()
    # sys.exit()


signal.signal(signal.SIGINT, sigint_handler)

if __name__ == '__main__':
    # if len(sys.argv) < 3:
    #     print("Invalid number of args")
    #     exit(1)
    # addr = (sys.argv[1], int(sys.argv[2]))
    logging.basicConfig(level=logging.DEBUG)

    # distribution thread
    distribution_thread = Thread(target=distribute_info)
    distribution_thread.start()

    addr = (config.server_ip, config.server_port)
    server = ThreadingHTTPServer(addr, HSRequestHandler)
    logging.info("serving requests from %s", addr)

    # start server
    server_thread = Thread(target=server.serve_forever)
    server_thread.start()

    server_thread.join()
    print('exiting')
    # server.serve_forever()
