import argparse
import asyncio
import os

loop = asyncio.get_event_loop()

ORDERER_ADDRESS = 'orderer.example.com'

def parse_args(verbose=True):
    executable = f'python {os.path.basename(__file__)}'
    parser = argparse.ArgumentParser(
        prog = executable,
        description = 'A tool for creating and joining channels in Fabric network (1.4.x)',
        epilog = executable
    )
    parser.add_argument('-s', '--settings', default=os.getenv('SETTINGS_DEFAULT') or 'settings/config-local.json')
    parser.add_argument('-c', '--channel', default='channel')
    parser.add_argument('-u', '--user', default='Admin@org1.example.com')

    parser.add_argument('-x', '--create', default=False, action='store_true')
    parser.add_argument('-j', '--join', nargs='*', default=[])

    args = parser.parse_args()

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

    if args.create:
        # Create a New Channel, the response should be true if succeed
        response = await client.channel_create(
            orderer=ORDERER_ADDRESS,
            requestor=user,
            channel_name=args.channel,
            config_yaml='fabric-network/configx',
            channel_profile='Channel'
        )
        print(response)

    for peer in args.join:
        # Join Peers into Channel, the response should be true if succeed
        org = peer.split('.', 1)[1]
        org_admin = client.get_user(org_name=org, name='Admin')
        responses = await client.channel_join(
            orderer=ORDERER_ADDRESS,
            requestor=org_admin,
            channel_name=args.channel,
            peers=[peer],
        )
        print(responses)

loop.run_until_complete(main())
