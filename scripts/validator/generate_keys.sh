#!/bin/bash

if [ $# -lt 2 ]; then
  echo "validator id and num of nodes required"
  exit 1
fi

id=$1
n=$2

# Create keys directory if not already created
if [[ ! -e "/private/keys" ]]; then
  echo "creating /private/keys directory"
  mkdir "/private/keys"
fi


# 1. Generate user keys if they do not already exist using 'sawtooth keygen'
if [[ ! -e "/private/keys/root.priv" ]]; then
  sawtooth keygen --key-dir "/private/keys" root
fi

# 2. Generate validator keys if they do not already exist using 'sawadm keygen'
if [[ ! -e "/private/keys/validator.priv" ]]; then
  echo "generating keys for validator $id"
  sawadm keygen --force
  cp /etc/sawtooth/keys/validator.priv /private/keys
  cp /etc/sawtooth/keys/validator.pub /private/keys
else
  cp /private/keys/validator.priv /etc/sawtooth/keys
  cp /private/keys/validator.pub /etc/sawtooth/keys
fi

# 3. Copy the validator public keys to shared directory for use by other
# validators
## Create the keys directory if not already present
if [[ ! -e "/shared/keys" ]]; then
  mkdir /shared/keys
fi

cp /private/keys/validator.pub "/shared/keys/validator-$id.pub"

# wait till all the public keys are available for use
for ((i=0; i<n; ++i))
do
  while [[ ! -f /shared/keys/validator-"$i".pub ]]
  do
    sleep 1
  done
done
