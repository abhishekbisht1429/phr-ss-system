import yaml

with open('config.yml') as config_file:
    config = yaml.safe_load(config_file)

_server = config['server']
server_ip = _server['ip']
server_port = _server['port']

_path = config['path']
keystore_path = _path['keystore']
hs_pub_key_path = _path['hs_pub_key']

_url = config['url']
registration_url = _url['registration']