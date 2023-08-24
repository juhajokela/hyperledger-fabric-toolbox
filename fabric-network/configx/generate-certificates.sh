#!/usr/bin/env bash
set -euo pipefail

# remove existing artifacts, or proceed on if the directories don't exist
rm -r "${PWD}"/crypto-config || true

# look for binaries in local dev environment /build/bin directory and then in local samples /bin directory
export PATH="${PWD}"/../../fabric/build/bin:"${PWD}"../../bin:"$PATH"

echo "Generating MSP certificates using cryptogen tool"
cryptogen generate --config="${PWD}"/crypto-config.yaml --output="${PWD}"/crypto-config
