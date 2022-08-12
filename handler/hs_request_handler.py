import base64
import http
import json
import hashlib

import util


def gen_phr(user_id):
    pass


def handle(path_components, data):
    """
    :param path_components: list
    :param msg: dict
    :return:
    """
    if len(path_components) < 1:
        return

    if path_components[0] == "phr_gen":
        #TODO: emulate the process of generating a PHR and run keyword
        # extraction algorithm on the PHR to derive the keywords

        print(data)

        #TODO: after generating phr and extracting keywords, encrypt the PHR
        # using the key provided by client and retrive the content id from
        # IPFS and send it to use after encrypting it along with encrypted
        # keywords

        # phr_id = base64.b64encode(b'some phr content id').decode('utf-8')
        # return http.HTTPStatus.OK, json.dumps({'phr_id_b64': phr_id,
        #                                        'keywords': ['some',
        #                                                     'demo',
        #                                                     'keywords']})

        phr_id = base64.b64encode(b'phr id 2').decode('utf-8')
        return http.HTTPStatus.OK, json.dumps({'phr_id_b64': phr_id,
                                               'keywords': ['some',
                                                            'demo',
                                                            'keywords',
                                                            'with',
                                                            'extras']})