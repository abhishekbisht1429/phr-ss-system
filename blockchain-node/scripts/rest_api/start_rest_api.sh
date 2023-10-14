#!/bin/bash

if [ $# -lt 4 ]; then
  echo "required - <rest_api container name> <validator_container_name> <validator
  port> <rest api port>"
  exit 1
fi

rest_api_container_name=$1
validator_container_name=$2
validator_port=$3
rest_api_port=$4

# Copy the config file to appropriate dir
if [[ -e /private/rest_api.toml ]]; then
  cp /private/rest_api.toml /etc/sawtooth
fi

sawtooth-rest-api -v \
  --connect tcp://"$validator_container_name":"$validator_port" \
  --bind "$rest_api_container_name":"$rest_api_port"