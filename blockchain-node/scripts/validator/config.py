import yaml
import os

with open('/shared/scripts/config.yml') as config_file:
    config = yaml.safe_load(config_file)

_path = config['path']
validator_key_dir = _path['validator']['key_dir']
validator_config_file = _path['validator']['config_file']
user_key_dir = _path['user']['key_dir']


_address = config['address']
kds_ip = _address['kds']['ip']
kds_port = _address['kds']['port']


_key = config['key']
network_pk = _key['network_pk']
network_sk = _key['network_sk']


_kds_url_segments = config['url']['kds']['segment']
kds_url = 'http://' + kds_ip + ':' + str(kds_port) \
          + '/' + _kds_url_segments['submit']