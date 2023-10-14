import pickle
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

from sawtooth_sdk.protobuf.events_pb2 import EventSubscription, EventFilter

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
import util


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
            res_code, data = patient_request_handler.handle(
                path_components[2:],
                data,
                phr_gen_event_listener
            )
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
    phr_gen_event_listener.stop_listening()
    util.Timer.stop_sync()
    server.shutdown()
    # sys.exit()


signal.signal(signal.SIGINT, sigint_handler)

if __name__ == '__main__':
    # if len(sys.argv) < 3:
    #     print("Invalid number of args")
    #     exit(1)
    # addr = (sys.argv[1], int(sys.argv[2]))
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    addr = (config.server_ip, config.server_port)
    server = HTTPServer(addr, HSRequestHandler)
    logging.info("serving requests from %s", addr)

    # Start search event listener
    search_subscription = EventSubscription(
        event_type='thesis/search_complete',
        filters=[EventFilter(
            key='id',
            # TODO: set the match_string to a specific value unique for
            #  the hospital
            match_string='.*',
            filter_type=EventFilter.REGEX_ANY
        )]
    )
    search_event_listener = bel.EventListener(config.validator_url,
                                              search_subscription)
    search_event_thread = Thread(target=search_event_listener.listen)
    search_event_thread.start()

    # Start phr generation event listener
    phr_gen_subscription = EventSubscription(
        event_type='thesis/phr_gen',
        filters=[EventFilter(
            key='id',
            # TODO: set the match_string to a specific value unique for
            #  the hospital
            match_string='.*',
            filter_type=EventFilter.REGEX_ANY
        )]
    )
    phr_gen_event_listener = bel.EventListener(config.validator_url,
                                               phr_gen_subscription)
    phr_gen_event_thread = Thread(target=phr_gen_event_listener.listen)
    phr_gen_event_thread.start()

    # start timer thread
    timer_thread = Thread(target=util.Timer.bg_sync)
    timer_thread.start()

    # start server
    server_thread = Thread(target=server.serve_forever)
    server_thread.start()

    search_event_thread.join()
    phr_gen_event_thread.join()
    timer_thread.join()
    server_thread.join()
    logging.info("Exiting")
    # server.serve_forever()
