#!/bin/bash

if [ $# -lt 1 ]; then
  echo "rest api id required"
  exit 1
fi

id=$1

# Copy the config file to appropriate dir
if [[ -e /private/rest_api.toml ]]; then
  cp /private/rest_api.toml /etc/sawtooth
fi

sawtooth-rest-api -v \
  --connect tcp://thesis-validator-"$id":4004 \
  --bind thesis-rest-api-"$id":8008