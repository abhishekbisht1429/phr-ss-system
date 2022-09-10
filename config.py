import yaml

with open('config.yml') as config_file:
    config = yaml.safe_load(config_file)

_path = config['path']
user_db_path = _path['user_db']
doc_db_path = _path['doc_db']
keystore_path = _path['keystore']

_server = config['server']
server_ip = _server['ip']
server_port = _server['port']

_blockchain_node = config['url']['blockchain_node']
batches_url = _blockchain_node['batches']
state_url = _blockchain_node['state']
validator_url = _blockchain_node['validator']

_doctor_device = config['url']['doctor']
phr_gen_seg = _doctor_device['phr_gen_seg']