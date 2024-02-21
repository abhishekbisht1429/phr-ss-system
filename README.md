# Introduction
This is a PHR storage and sharing system prototype that uses Blockchain, Searchable Symmetric Encryption and IPFS.

# Steps to run locally (Linux)

There are six components in this system listed as follows:
1. Blockchain Node
2. IPFS Node
3. Key Distribution Server
4. Doctor Device
5. Hospital Server
6. Client Device

To run the system locally on a linux system follow the steps given below:
1. Install docker on your system, if not already installed.
2. Copy the configuration files from `sample-configs` directories to the root of their respective component directories.

## Running Key distribution server
1. Run the key distribution server using `python3 server.py`. 
2. By default, it will run on `localhost:9005`.

## Running blockchain nodes
1. Replace `address->kds->ip` with the IP of your system in the `config.yml` file of the blockchain node component.
2. Run the blockchain nodes using `init.sh` command and supply the required parameters.
3. The gateway IP should be the IP of your system.
4. Give host-id as `0` and give the number of nodes as per your requirements (should be >= 4).

## Running IPFS nodes
1. Run the IPFS nodes using `init.sh` command in the component directory and supply the required parameters by 
   following the same rules as in the case of blockchain nodes.
2. Also specify the `--bootstrap` option.

## Running Doctor Device
1. Run doctor device using `python3 server.py`.
2. By default, it will run on `localhost:9001`.

## Running Hospital Server
1. Run hospital server by using `python3 server.py`
2. By default, it will run on `localhost:9000`.

## Running Client Device
1. Run client device using `python3 main.py`.
2. You will receive a prompt through which you can interact with the system. 

# Citation
Please cite the following Article if you intend to use any part of this codebase in your work.

[Efficient Personal-Health-Records Sharing in Internet of Medical Things Using Searchable Symmetric Encryption, Blockchain, and IPFS](https://doi.org/10.1109/OJCOMS.2023.3316922)

