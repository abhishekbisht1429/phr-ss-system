#!/bin/bash

if [[ $# -lt 3 ]]; then
  echo "Required argument - <host id> <number of nodes> <gateway ip>"
  exit 1
fi

host_id=$1
n=$2
gateway_ip=$3
# Create scripts dirs for validator
if [[ ! -d "./mount_binds/validator/shared/scripts" ]]; then
  mkdir -p "./mount_binds/validator/shared/scripts"
fi

# Create scripts dir for rest api
if [[ ! -d "./mount_binds/rest-api/shared/scripts" ]]; then
  mkdir -p "./mount_binds/rest-api/shared/scripts"
fi

# copy validator scripts
cp ./scripts/validator/config.py \
   ./scripts/validator/config.yml \
   ./scripts/validator/start_validator.py \
   ./scripts/validator/util.py \
   ./scripts/validator/init_validator.sh \
   ./cbor2 \
   "./mount_binds/validator/shared/scripts"

# Copy rest-api scripts
cp ./scripts/rest_api/start_rest_api.sh \
   "./mount_binds/rest-api/shared/scripts"


## Copy Configuration files
#for ((i=0; i<n; ++i))
#do
#  # Copy validator configuration file
#  if [[ ! -d "./mount_binds/validator/validator-$i" ]]; then
#    mkdir -p "./mount_binds/validator/validator-$i"
#  fi
#  cp ./config/validator/validator.toml \
#     ./mount_binds/validator/validator-"$i"
#
#  # Copy rest api configuration file
#  if [[ ! -d "./mount_binds/rest-api/rest-api-$i" ]]; then
#    mkdir -p "./mount_binds/rest-api/rest-api-$i"
#  fi
#
##  if [[ $i -eq 0 ]]; then
##    cp ./config/rest-api/rest_api.toml \
##       ./mount_binds/rest-api/rest-api-"$i"
##  fi
#done

## Create mount binds for grafana and influxdb
#
#if [[ ! -d ./mount_binds/grafana ]]; then
#  mkdir -p ./mount_binds/grafana
#fi
## workaround for grafana
#chmod o+w ./mount_binds/grafana
#
#
#if [[ ! -d ./mount_binds/influxdb ]]; then
#  mkdir -p ./mount_binds/influxdb
#fi
## copy the script to mount point
#cp ./scripts/influxdb/start_influxdb.sh ./mount_binds/influxdb


python3 docker_compose_generator.py "$host_id" "$n" "$gateway_ip"

docker-compose down --remove-orphans
docker container prune -y
docker-compose up
