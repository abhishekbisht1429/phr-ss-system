import subprocess
import sys
import os
import yaml

# TODO: Specify port mappings in quotes
PREFIX = 'thesis'


def generate_ports(host_id, node_index):
    ports = dict()

    # starting port number for this host
    first_host_port = 11000 + host_id * 500

    # 10 ports per node
    first_node_port = first_host_port + node_index * 10

    ports['validator_network'] = first_node_port
    ports['validator_component'] = first_node_port + 1
    ports["validator_consensus"] = first_node_port + 2

    ports['rest_api'] = first_node_port + 3
    ports['notif_receiver'] = first_node_port + 4

    return ports


def generate(host_id, n, gateway_ip):
    data = dict()
    data['version'] = '3.6'

    services = dict()
    for i in range(n):
        ports = generate_ports(host_id, i)

        # validator
        validator_container_name = PREFIX + '-validator-' + str(i)
        settings_tp_container_name = PREFIX + '-settings-tp-' + str(i)
        rest_api_container_name = PREFIX + '-rest-api-' + str(i)
        consensus_engine_container_name = PREFIX + '-consensus-engine-' + \
                                          str(i)
        tp_container_name = PREFIX + '-transaction-processor-' + str(i)

        validator = {
            'image': 'hyperledger/sawtooth-validator',
            'container_name': validator_container_name,
            'volumes':
                [
                    os.path.join(os.getcwd(), "mount_binds", "validator",
                                 "shared") + ":" + os.path.join("/", "shared")
                ],
            'command': 'bash /shared/scripts/init_validator.sh '
                       + validator_container_name + ' '
                       + gateway_ip + ' '
                       + str(ports['validator_network']) + ' '
                       + str(ports['validator_component']) + ' '
                       + str(ports['validator_consensus']) + ' '
                       + str(ports['notif_receiver']),
            'ports':
                [
                    str(ports['validator_network']) + ":"
                    + str(ports['validator_network']),

                    str(ports['notif_receiver']) + ":"
                    + str(ports['notif_receiver'])
                ]
        }

        # settings transaction processor
        settings_tp = {
            'image': 'hyperledger/sawtooth-settings-tp',
            'container_name': settings_tp_container_name,
            'depends_on': [validator_container_name],
            'command': 'settings-tp -v -C tcp://'
                       + validator_container_name + ':'
                       + str(ports['validator_component']),
        }

        # rest api
        rest_api = {
            'image': 'hyperledger/sawtooth-rest-api',
            'container_name': rest_api_container_name,
            'volumes':
                [
                    os.path.join(os.getcwd(), "mount_binds", "rest-api",
                                 "shared") + ':' + os.path.join("/", "shared"),
                    os.path.join(os.getcwd(), 'mount_binds', 'rest-api',
                                 'rest-api-' + str(i)) + ':' + os.path.join(
                        '/', 'private')
                ],
            'depends_on': [validator_container_name],
            'command': 'bash /shared/scripts/start_rest_api.sh '
                       + rest_api_container_name + ' '
                       + validator_container_name + ' '
                       + str(ports['validator_component']) + ' '
                       + str(ports['rest_api']),
            'ports':
                [
                    str(ports['rest_api']) + ":" + str(ports['rest_api'])
                ]
        }

        # consensus engine pbft
        consensus_engine = {
            'image': 'hyperledger/sawtooth-pbft-engine',
            'container_name': consensus_engine_container_name,
            'command': 'pbft-engine -v --connect tcp://'
                       + validator_container_name + ':'
                       + str(ports['validator_consensus']),
            'depends_on': [validator_container_name],
            # 'network_mode': 'host'
        }

        # transaction processor
        tp = {
            'image': 'thesis-tp',
            'container_name': tp_container_name,
            'command': 'python3 transaction_processor.py '
                       'tcp://' + validator_container_name + ':'
                       + str(ports['validator_component']),
            'depends_on': [validator_container_name],
            # 'network_mode': 'host'
        }

        services[validator_container_name] = validator
        services[settings_tp_container_name] = settings_tp
        services[rest_api_container_name] = rest_api
        services[consensus_engine_container_name] = consensus_engine
        services[tp_container_name] = tp
    data['services'] = services

    with open('compose.yml', 'w') as compose_file:
        yaml.dump(data, compose_file, default_style=False, sort_keys=False)


def main(args):
    host_id = int(args[0])
    n = int(args[1])
    gateway_ip = args[2]
    generate(host_id, n, gateway_ip)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('required - <host id> <number of nodes> <gateway ip>')
        exit(1)

    main(sys.argv[1:])
