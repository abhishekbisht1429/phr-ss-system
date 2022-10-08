#!/bin/bash

if [ $# -lt 5 ]; then
  echo "init requires - <host_ip> <gateway ip> <network_port> \
  <component_port> <consensus_port>"
  exit 1
fi

host_ip=$1
gateway_ip=$2
validator_network=$3
validator_component=$4
validator_consensus=$5


python3 /shared/scripts/start_validator.py "$host_ip" "$gateway_ip" \
        "$validator_network" "$validator_component" "$validator_consensus"