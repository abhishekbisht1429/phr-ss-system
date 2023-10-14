from http import HTTPStatus

import config
import util
import logging

bootstrap_list = list()

# NOTE: currently this function won't be used as there is no way to post data
# from BusyBox
def handle_post(path_components, raw_data):
    """
    :param path_components: list
    :param msg: dict
    :return:
    """
    if len(path_components) < 1:
        return HTTPStatus.NOT_FOUND, None

    if path_components[0] == "bootstrap":
        data = util.deserialize_obj(raw_data)
        bootstrap_node_info = {
            'ip': data['ip'],
            'id': data['id'],
            'port': data['port']
        }
        bootstrap_list.append(bootstrap_node_info)
        return HTTPStatus.OK, None
    else:
        return HTTPStatus.NOT_FOUND, None


def handle_get(path_components, headers):
    if len(path_components) < 1:
        return HTTPStatus.NOT_FOUND, None

    if path_components[0] == "bootstrap_list":
        # Generate response
        # NOTE: it would have been better to create the actual endpoint
        # strings at the ipfs node, however, due to limited functionality of
        # busy box we have to do it here and send the result back to it
        logging.debug("headers: " + str(headers))
        resp_str = ""
        for node_info  in bootstrap_list:
            resp_str += "/ip4/" + node_info['ip'] \
                        + "/tcp/" + node_info['port'] \
                        + "/p2p/" + node_info['id']
            resp_str += '\n'
        logging.debug("bootstrap list: " + resp_str)
        # NOTE: Receiving id and ip via GET Headers because BusyBox does
        # not support anything to post an HTTP request
        bootstrap_node_info = dict()
        bootstrap_node_info['ip'] = headers.get('IP')
        bootstrap_node_info['id'] = headers.get('ID')
        bootstrap_node_info['port'] = headers.get('PORT')

        logging.debug("received data: " + str(bootstrap_node_info))
        if bootstrap_node_info['id'] is not None:
            bootstrap_list.append(bootstrap_node_info)

        return HTTPStatus.OK, bytes(resp_str, encoding='utf-8')
    elif path_components[0] == "swarm_key":
        with open(config.swarm_key_path) as file:
            swarm_key = file.read()
        return HTTPStatus.OK, bytes(swarm_key, encoding='utf-8')
    else:
        return HTTPStatus.NOT_FOUND, None
