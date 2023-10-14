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
   ./config.yml \
   ./scripts/validator/start_validator.py \
   ./scripts/validator/util.py \
   ./scripts/validator/init_validator.sh \
   "./mount_binds/validator/shared/scripts"

# Copy rest-api scripts
cp ./scripts/rest_api/start_rest_api.sh \
   "./mount_binds/rest-api/shared/scripts"

python3 docker_compose_generator.py "$host_id" "$n" "$gateway_ip"

docker-compose down --remove-orphans
docker container prune -y
docker-compose up
