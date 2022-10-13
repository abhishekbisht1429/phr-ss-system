#!/bin/bash

# NOTE: this file just calls the python script init.py. I made it because I
# could not easily find a way to start an independent process from python script
if [ $# -lt 3 ]; then
  echo "input format - <host_index> <number of nodes> <gateway ip> " \
              "[--bootstrap]"
  exit
fi

host_index=$1
n=$2
gateway_ip=$3
opt=$4

# initialize
python3 init.py $host_index $n $gateway_ip $opt

docker-compose down --remove-orphans

# run the containers
docker-compose up



