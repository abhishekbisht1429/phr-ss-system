import yaml

with open('config.yml') as config_file:
    config = yaml.safe_load(config_file)

_path = config['path']
swarm_key_path = _path['ipfs']['swarm_key']

_server = config['server']
server_ip = _server['ip']
server_port = _server['port']

_blockchain_node = config['url']['blockchain_node']
batches_url = _blockchain_node['batches']
state_url = _blockchain_node['state']
validator_url = _blockchain_node['validator']

_doctor_device = config['url']['doctor']
phr_gen_seg = _doctor_device['phr_gen_seg']

# Total number of nodes for which the kds will wait for
total_nodes = config['total_nodes']