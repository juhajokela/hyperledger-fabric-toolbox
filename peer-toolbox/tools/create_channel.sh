#!/usr/bin/env sh
#
# SPDX-License-Identifier: Apache-2.0
#
set -eu

# create channel and add anchor peer
peer channel create -c $CH_NAME -o orderer.example.com:7050 -f "${PWD}"/config/channel-artifacts/channel.tx --outputBlock "${PWD}"/channel.block  --tls --cafile "${PWD}"/config/crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/tls/ca.crt
peer channel update -o orderer.example.com:7050 -c $CH_NAME -f "${PWD}"/config/channel-artifacts/Org1MSPanchors.tx --tls --cafile "${PWD}"/config/crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/tls/ca.crt

# join peer to channel
peer channel join -b "${PWD}"/channel.block