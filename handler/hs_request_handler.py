import base64
import http
import json
import hashlib
import tika
from tika import parser
import util

tika.initVM()

def extract_keywords(file_path):
    keywords = set()
    with open(file_path) as file:
        while True:
            line = file.readline()
            if not line:
                break
            for word in line.split():
                keywords.add(word)

    return list(keywords)


def gen_phr(file_path):
    keywords = extract_keywords(file_path)
    phr = bytearray()
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(512)
            if not data:
                break
            phr += data
    return phr


def handle(path_components, data):
    """
    :param path_components: list
    :param msg: dict
    :return:
    """
    if len(path_components) < 1:
        return

    if path_components[0] == "phr_gen":
        # TODO: emulate the process of generating a PHR and run keyword
        # extraction algorithm on the PHR to derive the keywords

        print(data)

        # TODO: after generating phr and extracting keywords, encrypt the PHR
        # using the key provided by client and retrive the content id from
        # IPFS and send it to use after encrypting it along with encrypted
        # keywords

        # phr_id = base64.b64encode(b'some phr content id').decode('utf-8')
        # return http.HTTPStatus.OK, json.dumps({'phr_id_b64': phr_id,
        #                                        'keywords': ['some',
        #                                                     'demo',
        #                                                     'keywords']})

        # phr_id = base64.b64encode(b'phr id 2').decode('utf-8')
        # return http.HTTPStatus.OK, json.dumps({'phr_id_b64': phr_id,
        #                                        'keywords': ['some',
        #                                                     'demo',
        #                                                     'keywords',
        #                                                     'with',
        #                                                     'extras']})
        user_id = data['user_id']

        file_path = './temp/' + user_id
        phr_id = util.bytes_to_b64(util.hash(file_path.encode('utf-8')))
        keywords = extract_keywords(file_path)

        return http.HTTPStatus.OK, json.dumps({'phr_id_b64': phr_id,
                                               'keywords': keywords})

if __name__ == '__main__':
    print(extract_keywords('../temp/user4'))
    print(gen_phr(('../temp/user1')))