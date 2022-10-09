import sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from threading import Thread

import config
import os.path
import urllib.parse as parse
import json
import logging
import signal

from handler import request_handler


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

        res_code, data = request_handler.handle(path_components[1:],
                                                            data)

        # return response to the server
        if res_code is not None:
            self.send_response(res_code, self.responses[res_code][0])
            self.end_headers()
            if data is not None:
                self.wfile.write(data)
        else:
            self.send_error(404)
            self.end_headers()

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

        res_code, data = request_handler.handle(path_components[1:])

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
    server.shutdown()
    # sys.exit()


signal.signal(signal.SIGINT, sigint_handler)

if __name__ == '__main__':
    # if len(sys.argv) < 3:
    #     print("Invalid number of args")
    #     exit(1)
    # addr = (sys.argv[1], int(sys.argv[2]))
    logging.basicConfig(level=logging.DEBUG)
    addr = (config.server_ip, config.server_port)
    server = ThreadingHTTPServer(addr, HSRequestHandler)
    logging.info("serving requests from %s", addr)

    # start server
    server_thread = Thread(target=server.serve_forever)
    server_thread.start()

    server_thread.join()
    print('exiting')
    # server.serve_forever()
