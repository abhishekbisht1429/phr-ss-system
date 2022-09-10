import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

import config
import os.path
import urllib.parse as parse
import json
import logging
from handler import external_request_handler, patient_request_handler, \
    doctor_request_handler
import keys
import blockchain_event_listener as bel
import signal


class HSRequestHandler(BaseHTTPRequestHandler):
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

        res_code = None
        if path_components[1] == "patient":
            res_code, data = patient_request_handler.handle(path_components[2:],
                                                            data)
        elif path_components[1] == "external":
            res_code, data = external_request_handler.handle(
                path_components[2:], data, search_event_listener)
        elif path_components[1] == "doctor":
            res_code, data = doctor_request_handler.handle(path_components[2:],
                                                           data)
            # data = data.encode() # internal communication happens on json

        # return response to the server
        if res_code is not None:
            self.send_response(res_code, self.responses[res_code][0])
            self.end_headers()
            if data is not None:
                self.wfile.write(data)
        else:
            self.send_error(404)
            self.end_headers()


def sigint_handler(signum, frame):
    logging.info("Shutting Down Server")
    search_event_listener.stop_listening()
    server.shutdown()
    # sys.exit()


signal.signal(signal.SIGINT, sigint_handler)

if __name__ == '__main__':
    # if len(sys.argv) < 3:
    #     print("Invalid number of args")
    #     exit(1)
    # addr = (sys.argv[1], int(sys.argv[2]))
    logging.basicConfig(level=logging.INFO)
    addr = (config.server_ip, config.server_port)
    server = HTTPServer(addr, HSRequestHandler)
    logging.info("serving requests from %s", addr)

    # Start event listener
    search_event_listener = bel.SearchEventListener(config.validator_url)
    event_thread = Thread(target=search_event_listener.listen)
    event_thread.start()

    # start server
    server_thread = Thread(target=server.serve_forever)
    server_thread.start()

    event_thread.join()
    server_thread.join()
    print('exiting')
    # server.serve_forever()
