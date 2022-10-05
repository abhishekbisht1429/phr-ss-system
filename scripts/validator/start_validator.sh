#!/bin/bash

if [ $# -lt 2 ]; then
  echo "validator id and num of nodes required"
  exit 1
fi

id=$1
n=$2

# generate keys
bash /shared/scripts/generate_keys.sh "$id" "$n"

# Create genesis block
if [[ $id == 0 ]]; then
  bash /shared/scripts/create_genesis_block.sh "$n"
  echo "Genesis Block created"
fi

# Copy off-chain configuration file to /etc/sawtooth
if [[ -e /private/validator.toml ]]; then
  cp /private/validator.toml /etc/sawtooth
  echo "copied validator off chain config file to /etc/sawtooth"
fi

peers=""
for ((i=0; i<id; ++i))
do
  peers+="tcp://thesis-validator-$i:8800"
  if [[ $i -lt $((id-1)) ]]; then
    peers+=","
  fi
done

if [[ -n $peers ]]; then
  peers="--peers "$peers
fi

echo $peers

sawtooth-validator -vvv \
  --bind component:tcp://eth0:4004 \
  --bind network:tcp://eth0:8800 \
  --bind consensus:tcp://eth0:5050 \
  --endpoint tcp://thesis-validator-"$id":8800 \
  $peers

