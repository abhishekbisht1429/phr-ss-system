import toml
import sys

NETWORK_ENDPOINT = "network:tcp://127.0.0.1:8800"
COMPONENT_ENDPOINT = "component:tcp://127.0.0.1:4004"
CONSENSUS_ENDPOINT = "consensus:tcp://127.0.0.1:5050"

NETWORK_PUBLIC_KEY = 'wFMwoOt>yFqI/ek.G[tfMMILHWw#vXB[Sv}>l>i)'
NETWORK_PRIVATE_KEY = 'r&oJ5aQDj4+V]p2:Lz70Eu0x#m%IwzBdP(}&hWM*'


def generate_config(host_id, validator_uid, peer_list=None):
    config = dict()
    config['bind'] = [
        NETWORK_ENDPOINT,
        COMPONENT_ENDPOINT,
        CONSENSUS_ENDPOINT
    ]

    config['endpoint'] = NETWORK_ENDPOINT
    config['peering'] = 'static'
    config['peers'] = peer_list
    config['scheduler'] = 'parallel'
    config['network_public_key'] = NETWORK_PUBLIC_KEY
    config['network_private_key'] = NETWORK_PRIVATE_KEY
    config['minimum_peer_connectivity'] = 3
    config['maximum_peer_connectivity'] = 100

    with open('validator.toml', 'w') as config_file:
        toml.dump(config, config_file)


if __name__ == '__main__':
    # if len(sys.argv) < 2:
    #     print('required format - <host id>')
    #     exit(1)
    # host_id = int(sys.argv[1])
    generate_config(0, 0)
