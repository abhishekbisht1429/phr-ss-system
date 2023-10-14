import yaml
import os

with open('config.yml') as config_file:
    config = yaml.safe_load(config_file)