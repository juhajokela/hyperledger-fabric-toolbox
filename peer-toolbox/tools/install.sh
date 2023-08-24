cd tools
apt update && apt install -y curl jq vim
curl -sSLO https://raw.githubusercontent.com/hyperledger/fabric/main/scripts/install-fabric.sh && chmod +x install-fabric.sh
./install-fabric.sh --fabric-version 1.4.6 binary
cd ..