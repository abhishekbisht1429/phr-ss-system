import logging
import requests
import keys
import util
import config


def register(doc_id, passwd, url):
    passwd_hash = util.hash(passwd.encode('utf-8'))
    enc_data = util.encrypt_obj(keys.hs_public_key(), {
        'doc_id': doc_id,
        'passwd_hash': passwd_hash,
        'pub_key': keys.public_key_sz(),
        'url': url
    })
    res = requests.post(config.registration_url, data=enc_data)

    if res.status_code == requests.codes.ok:
        logging.info("Registration successful")
    else:
        logging.error("Failed to register, code=", res.status_code)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    register('doc1', '1234', 'http://localhost:9001')