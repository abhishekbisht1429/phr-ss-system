import sys
import os
import yaml
import logging
import shutil
import subprocess
from config import config


def generate_addresses(node_index, host_index):
    addresses = dict()
    starting_host_port = 20000 + host_index * 200

    starting_node_port = starting_host_port + node_index * 5
    addresses['tcp'] = (config['node']['ip']['tcp'], starting_node_port + 1)
    addresses['gateway'] = (config['node']['ip']['gateway'], starting_node_port
                            + 2)
    # NOTE: rpc api must not be made available on public domain, however,
    # for development ease I am exposing it on all interfaces
    addresses['rpc_api'] = (config['node']['ip']['rpc'], starting_node_port + 3)

    return addresses


def generate_compose_file(n, host_id):
    services = dict()
    for i in range(n):
        addresses = generate_addresses(i, host_id)
        container = dict()
        container['image'] = 'ipfs/kubo'
        container['container_name'] = "ipfs-node-" + str(i)
        container['volumes'] = [
            os.path.join(os.getcwd(), 'mount_binds',
                         container['container_name'],
                         'ipfs_staging') + ':/export',

            os.path.join(os.getcwd(), 'mount_binds',
                         container['container_name'],
                         'ipfs_data') + ':/data/ipfs',

            os.path.join(os.getcwd(), 'mount_binds',
                         container['container_name'],
                         'container-init.d') + ':/container-init.d'
        ]
        container['ports'] = [
            addresses['tcp'][0] + ':' + str(addresses['tcp'][1]) + ':4001',
            addresses['gateway'][0] + ':' + str(addresses['gateway'][1]) +
            ':8080',
            addresses['rpc_api'][0] + ':' + str(addresses['rpc_api'][1]) +
            ':5001'
        ]

        # TODO: Find the proper documentation on how to set swarm key


        container['environment'] = {
            # Not required - will create a file directly in /data/ipfs/swarm key
            # 'IPFS_SWARM_KEY_FILE': '/shared/swarm.key'
            'IPFS_LOGGING': 'debug'
        }

        services[container['container_name']] = container

    data = {'services': services}

    with open('compose.yml', 'w') as compose_file:
        yaml.dump(data, compose_file)


def setup_host(n, host_index, gateway_ip, bootstrap):
    # Remove previous mount binds to start fresh
    if os.path.exists('./mount_binds'):
        shutil.rmtree('./mount_binds')

    # Create mount_binds on host machine
    for i in range(0, n):
        data_dir = os.path.join('mount_binds', 'ipfs-node-' + str(i),
                                'ipfs_data')
        staging_dir = os.path.join('mount_binds', 'ipfs-node-' + str(i),
                                   'ipfs_staging')
        init_scripts_dir = os.path.join('mount_binds',
                                        'ipfs-node-' + str(i),
                                        'container-init.d')
        scripts_dir = os.path.join(data_dir, 'scripts')

        # create the directories
        os.makedirs(data_dir)
        os.makedirs(staging_dir)
        os.makedirs(init_scripts_dir)
        os.mkdir(scripts_dir)

        # Copy scripts and replace any existing ones
        shutil.copy('scripts/init_node.sh', scripts_dir)
        # TODO: find a proper way to supply the url
        shutil.copy('scripts/kds_url.txt', scripts_dir)

        addresses = generate_addresses(i, host_index)
        with open(os.path.join(init_scripts_dir, '001-init.sh'), 'w') as file:
            file.write('#!/bin/sh\n')
            file.write('sh /data/ipfs/scripts/init_node.sh '
                       + str(addresses['tcp'][1]) + ' '
                       + gateway_ip + ' '
                       + ('--bootstrap' if bootstrap else ''))


def main(args):
    host_index = int(args[0])
    n = int(args[1])
    gateway_ip = args[2]
    if n < 1:
        logging.error('At least 1 node required')
        exit(1)

    if len(args) > 3 and args[3] == '--bootstrap':
        bootstrap = True
    else:
        bootstrap = False
    setup_host(n, host_index, gateway_ip, bootstrap)

    generate_compose_file(n, host_index)

    # # start containers
    # subprocess.run(['docker-compose', 'down', '--remove-orphans'])
    # subprocess.Popen(['docker-compose', 'up'], close_fds=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) < 4:
        print("required - <host_index> <number of nodes> <gateway ip> "
              "[--bootstrap]")
        exit()
    main(sys.argv[1:])
