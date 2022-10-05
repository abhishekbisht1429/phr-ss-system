import subprocess
import sys
import os
import yaml


# TODO: Specify port mappings in quotes
PREFIX = 'thesis'

def generate(n):
    data = dict()
    data['version'] = '3.6'

    services = dict()
    for i in range(n):
        # validator
        validator_container_name = PREFIX + '-validator-' + str(i)
        settings_tp_container_name = PREFIX + '-settings-tp-' + str(i)
        rest_api_container_name = PREFIX + '-rest-api-' + str(i)
        consensus_engine_container_name = PREFIX + '-consensus-engine-' + str(i)
        tp_container_name = PREFIX + '-transaction-processor-' + str(i)

        validator = {
            'image': 'hyperledger/sawtooth-validator',
            'container_name': validator_container_name,
            'volumes':
                [
                    os.path.join(os.getcwd(), "mount_binds", "validator",
                                 "shared") + ":" + os.path.join("/", "shared"),

                    os.path.join(os.getcwd(), "mount_binds", "validator",
                                 "validator-" + str(i)) + ':' +
                    os.path.join('/', 'private')
                ],

            'command': 'bash /shared/scripts/start_validator.sh '
                       + str(i) + ' ' + str(n),
            'ports': [str(4004 + i) + ":4004"]
        }
        services[validator_container_name] = validator

        # settings transaction processor
        settings_tp = {
            'image': 'hyperledger/sawtooth-settings-tp',
            'container_name': settings_tp_container_name,
            'depends_on': [validator_container_name],
            'command': 'settings-tp -v -C tcp://' + validator_container_name
                       + ':4004'
        }
        services[settings_tp_container_name] = settings_tp

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
            'command': 'bash /shared/scripts/start_rest_api.sh ' + str(i),
            'ports': [str(8008 + i) + ':8008']
        }
        services[rest_api_container_name] = rest_api

        # consensus engine pbft
        consensus_engine = {
            'image': 'hyperledger/sawtooth-pbft-engine',
            'container_name': consensus_engine_container_name,
            'command': 'pbft-engine -v --connect tcp://' +
                       validator_container_name + ':5050',
            'depends_on': [validator_container_name]
        }
        services[consensus_engine_container_name] = consensus_engine

        # transaction processor
        tp = {
            'image': 'thesis-tp',
            'container_name': tp_container_name,
            'command': 'python3 transaction_processor.py '
                       'tcp://' + validator_container_name + ':4004',
            'depends_on': [validator_container_name]
        }
        services[tp_container_name] = tp

    # stats
    influxdb_container_name = PREFIX + '-stats-influxdb'
    grafane_container_name = PREFIX + '-stats-grafana'
    influxdb = {
        'image': 'influxdb:1.8.10-alpine',
        'container_name': influxdb_container_name,
        'ports': ['8086:8086'],
        'volumes': [os.path.join(os.getcwd(), 'mount_binds', 'influxdb') +
                    ':' + os.path.join('/', 'var', 'lib', 'influxdb')],
        'entrypoint': 'bash /var/lib/influxdb/start_influxdb.sh'
    }

    grafana = {
        'image': 'grafana/grafana:latest',
        'container_name': grafane_container_name,
        'ports': ['3000:3000'],
        'volumes': [os.path.join(os.getcwd(), 'mount_binds', 'grafana') + ':'
                    + os.path.join('/', 'var', 'lib', 'grafana')]
    }
    services[influxdb_container_name] = influxdb
    services[grafane_container_name] = grafana

    data['services'] = services

    with open('compose.yml', 'w') as compose_file:
        yaml.dump(data, compose_file, default_style=False, sort_keys=False)


def main(args):
    n = int(args[0])
    generate(n)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('required - <number of nodes>')
        exit(1)

    main(sys.argv[1:])
