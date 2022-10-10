# Possible fixes for the peers not being listed problem
1. The peer list in the configuration of validator must contain adresses 
   that are visible to other validator nodes
2. The 'endpoint' key in the validator configuration should contain the 
   advertised endpoint i.e. the endpoint throught which other validators 
   will try to contact the current validator
3. Start the service that you want to be accessible on the exposed port on 
   the container_name instead of localhost (I need to verify if this is true)


# Other important notes
1. the 'bind' key must contain interface names like 'eth0', check the exact 
   format on sawtooth website
2. Try to reduce the number of intermediaries when passing data from a 
   source to destination
3. Only one of the nodes need to generate the genesis block so keep a proper 
   check.
4. Peer list does not have to contain all other members, when a validator 
   sends a connection request to another validator, the another validator 
   adds it to its peer list
5. Reduce the use of global variables but keep a check on what data is being 
   passed through functions

# Important points about Docker
1. To connect to a container port from host, expose it using the 'ports' key 
   in docker compose (check for docker run on internet)
2. To connect to a service running on host port, connect to the ip address 
   assigned to the host by the router for internet. (I still have to figure 
   this out properly)

# TODO
1. Figure out the working of docker bridge network
2. Figure out the internal working of docker. 
