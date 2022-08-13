import yaml

with open('config.yml') as config_file:
    config = yaml.safe_load(config_file)

hs_urls = config['url']['hospital_server']
hs_base_url = hs_urls['base']
hs_registration_url = hs_base_url + '/' + hs_urls['registration']
phr_gen_url = hs_base_url + '/' + hs_urls['phr_gen']
entries_url = hs_base_url + '/' + hs_urls['entries']
doc_ids_url = hs_base_url + '/' + hs_urls['doc_ids']

search_url = hs_base_url + '/' + hs_urls['search']

_path = config['path']
keystore_path = _path['keystore']
current_head_store_path = _path['current_head_store']
hs_public_key_path = _path['hs_public_key']
