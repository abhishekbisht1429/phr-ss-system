import yaml

with open('config.yml') as config_file:
    config = yaml.safe_load(config_file)

hospital_server_url = config['url']['hospital_server']
master_key_path = config['path']['master_key']
current_head_store_path = config['path']['current_head_store']
