import yaml

with open('config.yml') as config_file:
    config = yaml.safe_load(config_file)

_path = config['path']
user_db_path = _path['user_db']
doc_db_path = _path['doc_db']

_server = config['server']
server_ip = _server['ip']
server_port = _server['port']