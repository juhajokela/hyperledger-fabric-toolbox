import argparse
import asyncio
import os
import sys

from time import time

loop = asyncio.get_event_loop()

def parse_args(verbose=True):
    executable = f'python {os.path.basename(__file__)}'
    parser = argparse.ArgumentParser(
        prog = executable,
        description = 'A tool for deploying chaincode to Fabric network (1.4.x)',
        epilog = f'{executable} example v1.0'
    )
    parser.add_argument('operation')
    parser.add_argument('name')
    parser.add_argument('-a', '--init-args', nargs='*')

    version_default = 'rolling' if (1 < len(sys.argv) and sys.argv[1] == 'update') else 'v1.0'
    parser.add_argument('-v', '--version', default=version_default)
    parser.add_argument('-l', '--location')
    parser.add_argument('-e', '--endorsement-policy') # "OutOf(1, 'Org1MSP.member', 'Org2MSP.member', 'Org3MSP.member')"

    parser.add_argument('-s', '--settings', default=os.getenv('SETTINGS_DEFAULT') or 'settings/config-local.json')
    parser.add_argument('-p', '--peers', nargs='+', default=['peer0.org1.example.com'])
    parser.add_argument('-u', '--user')
    parser.add_argument('-c', '--channel', default='channel')

    args = parser.parse_args()

    if not args.user:
        args.user = f"Admin@{args.peers[0].split('.', 1)[1]}"

    if not args.location:
        args.location = args.name

    if args.version == 'rolling':
        args.version = str(int(time()))

    if verbose:
        print(args)
    return args

args = parse_args()

from hfc.fabric import Client
from hfc.util.policies import s2d

client = Client(net_profile=args.settings)

username, organization = args.user.split('@')
user = client.get_user(organization, username)

# Make the client know there is a channel in the network
client.new_channel(args.channel)

gopath = os.path.normpath(os.path.join(
    os.path.dirname(os.path.realpath('__file__')),
    'smart-contracts'
))
os.environ['GOPATH'] = os.path.abspath(gopath)


async def install(requestor, peers):
    responses = await client.chaincode_install(
        requestor=requestor,
        peers=peers,
        cc_path=args.location,
        cc_name=args.name,
        cc_version=args.version
    )

    print(responses)

    cc_name = args.name
    cc_version = args.version

    for response in (r.response for r in responses):
        if response.status == 200:
            continue
        if response.status == 500 and response.message == f'error installing chaincode code {cc_name}:{cc_version} (chaincode /var/hyperledger/production/chaincodes/{cc_name}.{cc_version} exists)':
            continue
        exit()


async def instantiate():
    policy = s2d().parse(args.endorsement_policy) if args.endorsement_policy else None
    print('endorsement policy:', policy)
    response = await client.chaincode_instantiate(
        requestor=user,
        channel_name=args.channel,
        peers=[args.peers[0]],
        args=args.init_args,
        cc_name=args.name,
        cc_version=args.version,
        cc_endorsement_policy=policy, # optional, but recommended
        wait_for_event=True # optional, for being sure chaincode is instantiated
    )
    print(response)


async def upgrade():
    policy = s2d().parse(args.endorsement_policy) if args.endorsement_policy else None
    print('endorsement policy:', policy)
    response = await client.chaincode_upgrade(
        requestor=user,
        channel_name=args.channel,
        peers=[args.peers[0]],
        args=args.init_args,
        cc_name=args.name,
        cc_version=args.version,
        cc_endorsement_policy=policy, # optional, but recommended
        wait_for_event=True # optional, for being sure chaincode is upgraded
    )
    print(response)


async def main():

    print('\n---\n')
    print('version:', args.version)

    if args.operation == 'install':
        await install(user, args.peers)

    if args.operation == 'instantiate':
        await instantiate()

    if args.operation == 'upgrade':
        await upgrade()

    if args.operation == 'init':
        for peer in args.peers:
            org = peer.split('.', 1)[1]
            _user = client.get_user(org, 'Admin')
            await install(_user, [peer])
        await instantiate()

    if args.operation == 'update':
        for peer in args.peers:
            org = peer.split('.', 1)[1]
            _user = client.get_user(org, 'Admin')
            await install(_user, [peer])
        await upgrade()


loop.run_until_complete(main())
