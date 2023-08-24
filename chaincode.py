import argparse
import asyncio
import os

loop = asyncio.get_event_loop()

def parse_args(verbose=True):
    executable = f'python {os.path.basename(__file__)}'
    parser = argparse.ArgumentParser(
        prog = executable,
        description = 'A tool for interacting with chaincode on Fabric network (1.4.x)',
        epilog = f'{executable} invoke CHAINCODE createEntry 101 0xdummy_data_1 0 0 0 | {executable} query CHAINCODE getEntry 101'
    )

    parser.add_argument('operation')
    parser.add_argument('chaincode_name')
    parser.add_argument('function')
    parser.add_argument('arguments', nargs='*')

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

# Make the client know there is a channel in the network
client.new_channel(args.channel)

username, organization = args.user.split('@')
user = client.get_user(organization, username)

async def main():

    print('\n---\n')

    if args.operation == 'query':
        try:
            # Query a chaincode
            response = await client.chaincode_query(
                requestor=user,
                channel_name=args.channel,
                peers=args.peers,
                fcn=args.function,
                args=args.arguments,
                cc_name=args.chaincode_name
            )
            # import json
            # from pprint import pprint
            # pprint(json.loads(response))
            print(response)
        except Exception as e:
            # print(e.args[0][0].response)
            raise e

    if args.operation == 'invoke':
        # Invoke a chaincode
        print('args:', args.arguments)
        response = await client.chaincode_invoke(
            requestor=user,
            channel_name=args.channel,
            peers=args.peers,
            fcn=args.function,
            args=args.arguments,
            cc_name=args.chaincode_name,
            wait_for_event=True, # for being sure chaincode invocation has been commited in the ledger, default is on tx event
            #cc_pattern='^invoked*' # if you want to wait for chaincode event and you have a `stub.SetEvent("invoked", value)` in your chaincode
        )
        print(type(response))
        print(dir(response))
        print(response)

loop.run_until_complete(main())