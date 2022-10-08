#!/bin/bash

if [ $# -lt 4 ]; then
  echo "required - <rest_api id> <host_ip> <validator port> <rest api port>"
  exit 1
fi

id=$1
host_ip=$2
validator_port=$3
rest_api_port=$4

# Copy the config file to appropriate dir
if [[ -e /private/rest_api.toml ]]; then
  cp /private/rest_api.toml /etc/sawtooth
fi

sawtooth-rest-api -v \
  --connect tcp://"$host_ip":"$validator_port" \
  --bind "$host_ip":"$rest_api_port"