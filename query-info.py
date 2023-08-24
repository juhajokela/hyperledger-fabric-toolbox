import argparse
import asyncio
import os

loop = asyncio.get_event_loop()

def parse_args(verbose=True):
    executable = f'python {os.path.basename(__file__)}'
    parser = argparse.ArgumentParser(
        prog = executable,
        description = 'A tool for querying info about Fabric network (1.4.x)',
        epilog = f'{executable} channels | {executable} chaincodes'
    )
    ops = ['channels', 'chaincodes', 'channel-info']
    parser.add_argument('operations', nargs='?', choices=ops, default=ops)

    parser.add_argument('-s', '--settings', default=os.getenv('SETTINGS_DEFAULT') or 'settings/config-local.json')
    parser.add_argument('-p', '--peers', nargs='+', default=['peer0.org1.example.com'])
    parser.add_argument('-u', '--user')
    parser.add_argument('-c', '--channel', default='channel')

    args = parser.parse_args()

    if not args.user:
        args.user = f"Admin@{args.peers[0].split('.', 1)[1]}"

    if verbose:
        print(args)
    return args

args = parse_args()

from hfc.fabric import Client
client = Client(net_profile=args.settings)

username, organization = args.user.split('@')
user = client.get_user(organization, username)

async def main():

    print('\n---\n')

    if 'channels' in args.operations:
        # Query Peer Joined channel
        print('CHANNELS')
        print(await client.query_channels(
            requestor=user,
            peers=args.peers,
            decode=True
        ))
        """
        # An example response:

        channels {
        channel_id: "businesschannel"
        }
        """

    if 'chaincodes' in args.operations:
        # Query Peer installed chaincodes, make sure the chaincode is installed
        print('CHAINCODES')
        print(await client.query_installed_chaincodes(
            requestor=user,
            peers=args.peers,
            decode=True
        ))
        """
        # An example response:

        chaincodes {
        name: "example_cc"
        version: "v1.0"
        path: "github.com/example_cc"
        id: "\374\361\027j(\332\225\367\253\030\242\303U&\356\326\241\2003|\033\266:\314\250\032\254\221L#\006G"
        }
        """

    if 'channel-info' in args.operations:
        print('CHANNEL INFO:', args.channel)
        client.new_channel(args.channel)
        print(await client.query_info(user, args.channel, args.peers))

loop.run_until_complete(main())