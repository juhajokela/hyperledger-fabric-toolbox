# Step -1: Get into the container
./activate.sh

# Step 0: Go to toolbox
cd toolbox

# [Step 0.5: Install prerequisites (only for fresh containers)]
./tools/install.sh

# Step 1: Set environment variables for config update
. tools/init_env.sh channel

# Step 2: Pull and translate the config
./tools/fetch-config.sh

# Step 3: Modify the config
./tools/edit-config.sh

# Step 4: Re-encode the config
./tools/encode-config.sh

# [Step 5: Get the Necessary Signatures (if any)]
. tools/activate-org1-admin.sh
peer channel signconfigtx -f config_update_in_envelope.pb

. tools/activate-org2-admin.sh
peer channel signconfigtx -f config_update_in_envelope.pb

. tools/activate-orderer-admin.sh
peer channel signconfigtx -f config_update_in_envelope.pb

# Step 6: Submit the config update transaction
./tools/submit-config.sh

# (for batch size & timeout updates activate orderer admin)
. tools/activate-orderer-admin.sh
./tools/submit-config.sh

# For more info, check:
- https://hyperledger-fabric.readthedocs.io/en/release-2.2/config_update.html
- https://medium.com/coinmonks/adding-updating-channel-capabilities-in-hyperledger-fabric-6cb2a1aaea21