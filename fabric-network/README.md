

# EXAMPLE CONFIG

CORE_PEER_TLS_ENABLED=true
CORE_PEER_GOSSIP_USELEADERELECTION=true
CORE_PEER_GOSSIP_ORGLEADER=false
CORE_PEER_PROFILE_ENABLED=true

CORE_PEER_TLS_CERT_FILE=/etc/hyperledger/fabric/tls/server.crt
CORE_PEER_TLS_KEY_FILE=/etc/hyperledger/fabric/tls/server.key
CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/fabric/tls/ca.crt

CORE_PEER_ID=peer0.org1.example.com

CORE_PEER_ADDRESS=peer0.org1.example.com:7051
CORE_PEER_LISTENADDRESS=0.0.0.0:7051

CORE_PEER_CHAINCODEADDRESS=peer0.org1.example.com:7052
CORE_PEER_CHAINCODELISTENADDRESS=0.0.0.0:7052

CORE_PEER_GOSSIP_BOOTSTRAP=peer0.org1.example.com:7051
CORE_PEER_GOSSIP_EXTERNALENDPOINT=peer0.org1.example.com:7051

# EXPLANATIONS

CORE_PEER_ADDRESS
represents the endpoint to other peers in the same organization

CORE_PEER_LISTENADDRESS
the Address at local network interface this Peer will listen on (i.e. for sdk?)
(will be passed to the chaincode container to look for the Peer)

CORE_PEER_CHAINCODELISTENADDRESS
???
(will be passed to the chaincode container to look for the Peer)

CORE_PEER_GOSSIP_BOOTSTRAP
Is used to bootstrap gossip within an organization. If you are using gossip, you will typically configure all the peers in your org to point to an initial set of peers for bootstrap (you can specific a space-separated list of peers). Off course peers can bootstrap from different peers as well, but in that case you just need to make sure that there's a bootstrap path across all peers. Peers within an organization will typically communicate on their internal endpoints (meaning you do not have to expose all the peers in an org publicly). When the peer contacts the bootstrap peer, it passes it's endpoint info and then gossip is used to distribute the info about all the peers in the organization among the peers in the organization.

CORE_PEER_GOSSIP_EXTERNALENDPOINT
In order for peers to communicate across organizations, again some type of bootstrap information is required. The initial cross-organization bootstrap information is provided via the "anchor peers" setting in the channel configuration. This allows peers who have joined a channel to discover other peers on the channel as well. But clearly initially a peer in on organization will only know about the anchor peers for there organizations. If you want to make other peers in your organization known to other organizations, then you need to set this property. If this is not set, then the endpoint information about the peer will not be broadcast to peers in other organizations, and in fact - that peer will only be known to its own organization.