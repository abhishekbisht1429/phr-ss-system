#!/bin/sh

echo "configuring node"

# TODO: use getopts to parse the options
if [ $# -lt 2 ]; then
  echo "required format - <port> <gateway_ip> [--bootstrap]"
fi

port=$1
gateway_ip=$2
opt=$3

# TODO: put the url in a config file and load it
kds_base_url="http://192.168.1.184:9000/ipfs"
bootstrap_list_url="$kds_base_url/bootstrap_list"
swarm_key_url="$kds_base_url/swarm_key"

swarm_key_path="/data/ipfs/swarm.key"
bootstrap_list_path="/tmp/bootstrap_list"

# Download the bootstrap list
if [ $opt = "--bootstrap" ]; then
  echo "bootstrap request outgoing"
  id=$(ipfs id -f="<id>")
  wget -O "$bootstrap_list_path" "$bootstrap_list_url" \
        --header="IP: $gateway_ip" \
        --header="PORT: $port" \
        --header="ID: $id"
else
  wget -O /tmp/bootstrap_list "$bootstrap_list_url"
fi

# Download the swarm key
# TODO: find the documentation on how to set swarm key
wget -O "$swarm_key_path" "$swarm_key_url"

# remove default bootstrap nodes
ipfs bootstrap rm all

# add private bootstrap nodes
while read -r peer_addr; do
  ipfs bootstrap add $peer_addr
done < $bootstrap_list_path
