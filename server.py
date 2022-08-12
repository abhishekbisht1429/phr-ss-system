from http.server import HTTPServer, BaseHTTPRequestHandler

import config
import os.path
import urllib.parse as parse
import json
import logging
from handler import hs_request_handler

# Assuming that this sever is running on local network of the hospital
# TODO: Find a way to secure the communication between HS and doctor device
#  server. Push notification kind of technology maybe ?
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
            data = json.loads(self.rfile.read(content_len))

        res_code = None
        if path_components[1] == "hs":
            res_code, data = hs_request_handler.handle(path_components[2:],
                                                            data)

        # return response to the server
        if res_code is not None:
            self.send_response(res_code, self.responses[res_code][0])
            self.end_headers()
            if data is not None:
                self.wfile.write(data.encode())
        else:
            self.send_error(404)
            self.end_headers()


if __name__ == '__main__':
    # if len(sys.argv) < 3:
    #     print("Invalid number of args")
    #     exit(1)
    # addr = (sys.argv[1], int(sys.argv[2]))
    logging.basicConfig(level=logging.INFO)
    addr = (config.server_ip, config.server_port)
    server = HTTPServer(addr, HSRequestHandler)
    logging.info("serving requests from %s", addr)
    server.serve_forever()
