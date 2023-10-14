from http import HTTPStatus
import util
import config


def handle(path_components, raw_data, node_info_list, distribute_condition):
    """
    :param path_components: list
    :param msg: dict
    :return:
    """
    if len(path_components) < 1:
        return HTTPStatus.NOT_FOUND, None

    if path_components[0] == "submit":
        data = util.deserialize_obj(raw_data)
        with distribute_condition:
            node_info_list.append({
                'gateway_ip': data['gateway_ip'],
                'validator_port': data['validator_port'],
                'pk': data['pk'],
                'notif_receiver_port': data['notif_receiver_port']
            })
            if len(node_info_list) == config.total_nodes:
                distribute_condition.notify_all()
        return HTTPStatus.OK, None
    else:
        return HTTPStatus.NOT_FOUND, None
