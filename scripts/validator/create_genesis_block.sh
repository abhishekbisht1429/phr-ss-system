#!/bin/bash

if [[ $# -lt 1 ]]; then
  echo "required parameter - number of nodes"
  exit 1
fi

n=$1

sawset genesis --key /private/keys/root.priv -o config-genesis.batch

member_keys=""
for ((i=0; i<n; ++i))
do
  member_key=($(cat /shared/keys/validator-"$i".pub))
  if [[ $i -eq 0 ]]; then
    member_keys+="["
  fi
  member_keys+="\"$member_key\""

  if [[ $i -eq $((n-1)) ]]; then
    member_keys+="]"
  else
    member_keys+=","
  fi
done

echo $member_keys

sawset proposal create --key /private/keys/root.priv -o config-consensus.batch \
        sawtooth.consensus.algorithm.name=pbft \
        sawtooth.consensus.algorithm.version=1.0 \
        sawtooth.consensus.pbft.members="$member_keys" \
        sawtooth.consensus.pbft.block_publishing_delay=0

sawadm genesis config-genesis.batch config-consensus.batch