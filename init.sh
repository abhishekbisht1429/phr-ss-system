#!/bin/bash

if [[ $# -lt 1 ]]; then
  echo "Required argument - <number of nodes>"
  exit 1
fi

n=$1
# Create scripts dirs
if [[ ! -d "./mount_binds/validator/shared/scripts" ]]; then
  mkdir -p "./mount_binds/validator/shared/scripts"
fi

if [[ ! -d "./mount_binds/rest-api/shared/scripts" ]]; then
  mkdir -p "./mount_binds/rest-api/shared/scripts"
fi

# copy scripts
cp ./scripts/validator/create_genesis_block.sh \
   ./scripts/validator/generate_keys.sh \
   ./scripts/validator/start_validator.sh \
   "./mount_binds/validator/shared/scripts"

cp ./scripts/rest_api/start_rest_api.sh \
   "./mount_binds/rest-api/shared/scripts"


# Copy Configuration files
for ((i=0; i<n; ++i))
do
  # Copy validator configuration file
  if [[ ! -d "./mount_binds/validator/validator-$i" ]]; then
    mkdir -p "./mount_binds/validator/validator-$i"
  fi
  cp ./config/validator/validator.toml \
     ./mount_binds/validator/validator-"$i"

  # Copy rest api configuration file
  if [[ ! -d "./mount_binds/rest-api/rest-api-$i" ]]; then
    mkdir -p "./mount_binds/rest-api/rest-api-$i"
  fi

#  if [[ $i -eq 0 ]]; then
#    cp ./config/rest-api/rest_api.toml \
#       ./mount_binds/rest-api/rest-api-"$i"
#  fi
done

# Create mount binds for grafana and influxdb

if [[ ! -d ./mount_binds/grafana ]]; then
  mkdir -p ./mount_binds/grafana
fi
# workaround for grafana
chmod o+w ./mount_binds/grafana


if [[ ! -d ./mount_binds/influxdb ]]; then
  mkdir -p ./mount_binds/influxdb
fi
# copy the script to mount point
cp ./scripts/influxdb/start_influxdb.sh ./mount_binds/influxdb


python3 docker_compose_generator.py "$n"

docker-compose down --remove-orphans

docker-compose up
