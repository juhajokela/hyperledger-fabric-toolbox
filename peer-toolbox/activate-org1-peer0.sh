docker cp dummy peer0.org1.example.com:toolbox
docker cp tools peer0.org1.example.com:toolbox/tools
docker cp ../fabric-network/configx peer0.org1.example.com:toolbox/config
docker exec -it peer0.org1.example.com bash