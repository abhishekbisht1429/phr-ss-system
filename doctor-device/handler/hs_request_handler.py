import http
import tika
from cryptography.hazmat.primitives import serialization
import logging
import ipfs_client
import keys
import util

tika.initVM()


def extract_keywords(file_path):
    with util.Timer('extract_keywords', file_path):
        keywords = set()
        with open(file_path) as file:
            while True:
                line = file.readline()
                if not line:
                    break
                for word in line.split():
                    keywords.add(word)
        logging.debug('num of keywords: {}'.format(len(keywords)))
        return list(keywords)


def gen_phr(file_path):
    with util.Timer('gen_phr', file_path):
        phr = bytearray()
        with open(file_path, 'rb') as file:
            while True:
                data = file.read(512)
                if not data:
                    break
                phr += data
        return phr


def handle(path_components, raw_data):
    """
    :param path_components: list
    :param msg: dict
    :return:
    """
    if len(path_components) < 1:
        return

    if path_components[0] == "phr_gen":
        data = util.decrypt_obj(keys.private_key(), raw_data)
        with util.Timer('phr_gen', data['user_id']):
            # TODO: emulate the process of generating a PHR and run keyword
            # extraction algorithm on the PHR to derive the keywords

            logging.debug(data)

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
            doc_enc_key = util.decrypt_obj(keys.private_key(), data['doc_enc_key'])
            user_pub_key = serialization.load_pem_public_key(data['user_pub_key'])

            # encrypt the phr
            file_path = './temp/' + user_id
            enc_file_path = './temp/encrypted_files' + user_id
            util.encrypt_file(file_path, enc_file_path, doc_enc_key)

            # upload the phr to IPFS
            with util.Timer('phr_upload'):
                status_code, data = ipfs_client.add(enc_file_path)
                if status_code != http.HTTPStatus.OK:
                    return http.HTTPStatus.INTERNAL_SERVER_ERROR, None

            # phr_id = util.bytes_to_b64(util.hash(file_path.encode('utf-8')))
            phr_id = data['Hash'].encode('utf-8')

            # Extract the keywords
            keywords = extract_keywords(file_path)
            res_data = util.encrypt_obj(user_pub_key, {
                'phr_id': phr_id,
                'keywords': keywords
            })
            return http.HTTPStatus.OK, res_data


if __name__ == '__main__':
    print(extract_keywords('../temp/regis'))
    print(gen_phr(('../temp/user1')))
