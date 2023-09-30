# hyperledger-fabric-toolbox

A tooling for interacting with Hyperledger Fabric.
Developed due to lack of proper tooling for Hyperledger Fabric.
There are basically just shell scripts available.

The tooling was developed alongside a research project utilising Hyperledger Fabric.
This is a generalisation of the tooling, and thus the code base is not fully verified.

## Contents
- [Prerequisites](#prerequisites)
- [Usage](#usage)
  * [Start Network](#start-network)
  * [Stop Network](#stop-network)
  * [Start docker environment for running the sdk](#start-docker-environment-for-running-the-sdk)
  * [Create channel (& join)](#create-channel--join)
  * [Develop smart contract (chaincode)](#develop-smart-contract-chaincode)
  * [Deploy smart contract (chaincode)](#deploy-smart-contract-chaincode)
  * [Play with it](#play-with-it)
  * [Usage Tips](#usage-tips)
  * [Multi-host Setup](#multi-host-setup)
- [Todo](#todo)

## Prerequisites

- Docker
- Docker Compose

## Usage

### Start Network

If running on ARM-based Mac:
```
export DOCKER_DEFAULT_PLATFORM=linux/amd64
```

**Create docker network:**
```
docker network create fabric-network
```

**1 org & 1 peer:**
```
HLF_VERSION=1.4.12 docker-compose -f fabric-network/docker-compose-org1-and-orderer.yaml up
```

**2 orgs (1 peer each):**
```
HLF_VERSION=1.4.12 docker-compose -f fabric-network/docker-compose-2orgs.yaml up
```

**3 orgs (1 peer each):**
```
HLF_VERSION=1.4.12 docker-compose -f fabric-network/docker-compose-3orgs.yaml up
```

**3 orgs (1 peer each) on separate hosts:**
```
# host 1
HLF_VERSION=1.4.12 docker-compose -f fabric-network/docker-compose-org1-and-orderer.yaml up

# host 2
HLF_VERSION=1.4.12 docker-compose -f fabric-network/docker-compose-org2.yaml up

# host 3
HLF_VERSION=1.4.12 docker-compose -f fabric-network/docker-compose-org3.yaml up
```

Also, check [Multi-host setup](#multi-host-setup).

### Stop Network

Ctrl-C / Cmd-C to stop

### Start docker environment for running the sdk

If running on ARM-based Mac:
```
export DOCKER_DEFAULT_PLATFORM=linux/amd64
```

NOTE! Run "build" only first time.

```
./sdk-docker/build.sh
```

```
./sdk-docker/run.sh
```

NOTE! Must be run from the root directory for everything to work.

### Create channel (& join)

```
python manage-channels.py --create --join peer0.org1.example.com

python manage-channels.py --create --join peer0.org1.example.com peer0.org2.example.com peer0.org3.example.com
```

https://hyperledger-fabric.readthedocs.io/en/release-1.4/build_network.html#create-join-channel

### Develop smart contract (chaincode)

https://hyperledger-fabric.readthedocs.io/en/release-1.4/chaincode4ade.html
https://pkg.go.dev/github.com/hyperledger/fabric/core/chaincode/shim

### Deploy smart contract (chaincode)

#### The shortcut way

initialize
```
# 1 org & 1 peer
python deploy-chaincode.py init CHAINCODE -a Admin@org1.example.com 1 5 5

# 3 orgs & 3 peers
python deploy-chaincode.py init CHAINCODE -a Admin@org1.example.com,Admin@org2.example.com,Admin@org3.example.com 1 5 5 -p peer0.org1.example.com peer0.org2.example.com peer0.org3.example.com

python deploy-chaincode.py init CHAINCODE -e "OutOf(1, 'Org1MSP.member', 'Org2MSP.member', 'Org3MSP.member')" -a Admin@org1.example.com,Admin@org2.example.com,Admin@org3.example.com 1 5 5 -p peer0.org1.example.com peer0.org2.example.com peer0.org3.example.com
```

update
```
# 1 org & 1 peer
python deploy-chaincode.py update CHAINCODE -a Admin@org1.example.com 1 5 5

# 2 orgs & 2 peers
python deploy-chaincode.py update CHAINCODE -e "OutOf(1, 'Org1MSP.member', 'Org2MSP.member')"  -a Admin@org1.example.com,Admin@org2.example.com 1 5 5 -p peer0.org1.example.com peer0.org2.example.com

# 3 orgs & 3 peers
python deploy-chaincode.py update CHAINCODE -e "OutOf(1, 'Org1MSP.member', 'Org2MSP.member', 'Org3MSP.member')"  -a Admin@org1.example.com,Admin@org2.example.com,Admin@org3.example.com 1 5 5 -p peer0.org1.example.com peer0.org2.example.com peer0.org3.example.com
```

#### The manual way

initialize
```
# 1 org & 1 peer
VERSION="$(date +%s)"
python deploy-chaincode.py install CHAINCODE
python deploy-chaincode.py instantiate CHAINCODE -a Admin@org1.example.com 1 5 5

# 2 orgs & 2 peers
python deploy-chaincode.py install CHAINCODE
python deploy-chaincode.py install CHAINCODE -u Admin@org2.example.com -p peer0.org2.example.com
python deploy-chaincode.py instantiate CHAINCODE  -e "OutOf(2, 'Org1MSP.member', 'Org2MSP.member')" -a Admin@org1.example.com,Admin@org2.example.com 1 5 5
```

update
```
# 1 org & 1 peer
python deploy-chaincode.py install CHAINCODE
python deploy-chaincode.py upgrade CHAINCODE -a Admin@org1.example.com 1 5 5

# 2 orgs & 2 peers
python deploy-chaincode.py install CHAINCODE
python deploy-chaincode.py install CHAINCODE -u Admin@org2.example.com -p peer0.org2.example.com
python deploy-chaincode.py upgrade CHAINCODE  -e "OutOf(2, 'Org1MSP.member', 'Org2MSP.member')" -a Admin@org1.example.com,Admin@org2.example.com 1 5 5
```

https://hyperledger-fabric.readthedocs.io/en/release-1.4/build_network.html#install-instantiate-chaincode
https://hyperledger-fabric.readthedocs.io/en/release-1.4/endorsement-policies.html

### Play with it

```
python query-info.py

python chaincode.py query CHAINCODE getEntry 101
python chaincode.py invoke CHAINCODE createEntry 101 0xdummy_data_1 0 0 0
python chaincode.py query CHAINCODE getEntry 101

DATE="$(date +%s)";python chaincode.py invoke CHAINCODE createEntry $DATE 0xdummy_data_1 0 0 0
```

### Usage Tips

#### Set policy on deploying chaincode
export PATH=${PATH}:${PWD}/bin
python3 deploy-chaincode.py CHAINCODE init -c businesschannel -e "OutOf(1, 'Org1MSP.member', 'Org2MSP.member')" -a Admin@org1.example.com,Admin@org2.example.com ARG1 ARG2 ...

#### Set bin to path
cd hyperledger-fabric-toolbox/
export PATH=${PATH}:${PWD}/bin
python3 deploy-chaincode.py CHAINCODE install -c businesschannel -v 1 -u Admin@org1.example.com -p peer0.org1.example.com

#### Use pseudo random arguments
DATE="$(date +%s)";python3 chaincode.py invoke CHAINCODE FUNCTION $DATE ARG2 ...

#### Listen events
python3 event-listener.py -c businesschannel -u Admin@org2.example.com -p peer0.org2.example.com

### Multi-host Setup

https://kctheservant.medium.com/multi-host-setup-with-raft-based-ordering-service-29730788b171

For multiple machines to communicate together as a swarm using overlay, docker requires the following ports to be open between the hosts:
- TCP port 2377 for cluster management communications
- TCP and UDP port 7946 for communication among nodes
- UDP port 4789 for overlay network traffic

#### host 1

```
docker swarm init --advertise-addr XXX.XXX.XXX.XXX
docker swarm join-token manager
```

#### host 2

```
docker swarm join --token SWMTKN-1-0z9iumdwiguuz2assgvt0jr2yo6cda2jljl3us6u9v986gs9hf-dn8deilo0ltlzm5cb0r9tk9ep 195.148.124.142:2377 --advertise-addr 3.70.185.229
```

#### host 1

```
docker network create --attachable --driver overlay fabric-network
docker network ls # optional
```

#### host 2

```
docker network ls # optional
```

#### on host 1&2

```
export DOCKER_DEFAULT_PLATFORM=linux/amd64
docker system prune --volumes

docker network create --attachable --driver overlay fabric-network
export HLF_VERSION=1.4.12
docker-compose -f fabric-network/docker-compose-org1-and-orderer.yaml up
```

## Todo

- try to cleanup peers.eventUrl and peers.grpcOptions
- fix chaincode endorsement policy
- make rest of the settings configurable in create-and-join-channels and deploy-chaincode
- interactive shell: cli.py with parser.parse_args(input("> "))
- more flexible way to setup fabric network with different configurations
- think about deploy script again - two different procedures: init & update
- let's test if endorsement policy strings work without parsing
- rename fabric-network -> network and replace all "fabric-network" references in files

- add to documentation:
    - https://hyperledger-fabric.readthedocs.io/en/release-1.4/channel_update_tutorial.html
    - https://hyperledger-fabric.readthedocs.io/en/release-1.4/endorsement-policies.html

- could we skip using chaincode endorsement policies? (seems to be so)

- -s --settings -> -net --network (now both are used in a mixed up way)

- _channel-artifacts & channel-artifacts - delete either one of them
