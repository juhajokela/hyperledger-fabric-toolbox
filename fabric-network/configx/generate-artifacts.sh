#!/usr/bin/env bash
set -euo pipefail

SYS_CHANNEL=testchainid
ORDERER_GENESIS_PROFILE=OrdererGenesisSolo
CHANNEL=channel
CHANNEL_PROFILE=Channel

# remove existing artifacts, or proceed on if the directories don't exist
rm -r "${PWD}"/channel-artifacts || true

# look for binaries in local dev environment /build/bin directory and then in local samples /bin directory
export PATH="${PWD}"/../../fabric/build/bin:"${PWD}"/../../bin:"$PATH"

# set FABRIC_CFG_PATH to configtx.yaml directory that contains the profiles
export FABRIC_CFG_PATH="${PWD}"

echo "Generating orderer genesis block"
mkdir channel-artifacts # pre-process
configtxgen -profile ${ORDERER_GENESIS_PROFILE} -channelID ${SYS_CHANNEL} -outputBlock channel-artifacts/genesis.block

echo "Generating channel create config transaction"
configtxgen -profile ${CHANNEL_PROFILE} -channelID ${CHANNEL} -outputCreateChannelTx channel-artifacts/channel.tx

echo "Generating anchor peer update transaction for Org1"
configtxgen -profile ${CHANNEL_PROFILE} -outputAnchorPeersUpdate channel-artifacts/Org1MSPanchors.tx -channelID channel -asOrg Org1MSP

echo "Generating anchor peer update transaction for Org2"
configtxgen -profile ${CHANNEL_PROFILE} -outputAnchorPeersUpdate channel-artifacts/Org2MSPanchors.tx -channelID channel -asOrg Org2MSP

echo "Generating anchor peer update transaction for Org3"
configtxgen -profile ${CHANNEL_PROFILE} -outputAnchorPeersUpdate channel-artifacts/Org3MSPanchors.tx -channelID channel -asOrg Org3MSP
