import shelve
from http import HTTPStatus

import config
import keys
import util


def handle(path_components, raw_data):
    """
    :param path_components: list
    :param msg: dict
    :return:
    """
    if len(path_components) < 1:
        return

    if path_components[0] == "registration":
        data = util.decrypt_obj(keys.server_ec_priv_key(), raw_data)

        with shelve.open(config.doc_db_path) as doc_db:
            doc_db[data['doc_id']] = {'pub_key': data['pub_key'],
                                      'passwd_hash': data['passwd_hash'],
                                      'url': data['url']}
            return HTTPStatus.OK, None
    else:
        return HTTPStatus.NOT_FOUND, None
