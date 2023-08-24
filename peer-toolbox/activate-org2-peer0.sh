docker cp dummy peer0.org2.example.com:toolbox
docker cp tools peer0.org2.example.com:toolbox/tools
docker cp ../fabric-network/configx peer0.org2.example.com:toolbox/config
docker exec -it peer0.org2.example.com bash