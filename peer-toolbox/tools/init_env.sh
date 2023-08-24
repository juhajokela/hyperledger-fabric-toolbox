if [ "$#" -ne 1 ]
then
  echo "Usage: . tools/init_env.sh channel"
else
  export PATH="$PATH:$(pwd)/tools/bin"
  export TLS_ROOT_CA=/toolbox/config/crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem
  export ORDERER_CONTAINER=orderer.example.com:7050
  export CH_NAME=$1
fi
