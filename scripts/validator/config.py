import yaml
import os

with open('/shared/scripts/config.yml') as config_file:
    config = yaml.safe_load(config_file)

_path = config['path']
validator_key_dir = _path['validator']['key_dir']
validator_config_file = _path['validator']['config_file']
user_key_dir = _path['user']['key_dir']


_address = config['address']
server_ip = _address['server']['ip']
server_port = _address['server']['port']

kds_ip = _address['kds']['ip']
kds_port = _address['kds']['port']

# network_ip = _address['network']['ip']
# network_port = _address['network']['port']
#
# component_ip = _address['component']['ip']
# component_port = _address['component']['port']
#
# consensus_ip = _address['consensus']['ip']
# consensus_port = _address['consensus']['port']

# network_endpoint = 'network:tcp://'+config.network_ip+':'+\
#                    str(config.network_port)
# component_endpoint = 'component:tcp://'+config.component_ip+':'\
#                      + str(config.component_port)
# consensus_endpoint = 'consensus:tcp://'+config.consensus_ip+':'+\
#                      str(config.consensus_port)


_key = config['key']
network_pk = _key['network_pk']
network_sk = _key['network_sk']


_url = config['url']
kds_url = _url['key_distribution_server']['submit']