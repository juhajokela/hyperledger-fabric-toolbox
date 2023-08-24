import argparse
import asyncio
import copy
import os
import time

loop = asyncio.get_event_loop()

def parse_args(verbose=True):
    executable = f'python {os.path.basename(__file__)}'
    parser = argparse.ArgumentParser(
        prog = executable,
        description = 'A tool for benchmarking chaincode (function)',
        epilog = f'{executable} 50'
    )

    parser.add_argument('parallelism')

    parser.add_argument('-n', '--network', default=os.getenv('CONFIG_DEFAULT') or 'settings/config-local.json')
    parser.add_argument('-p', '--peers', nargs='+', default=['peer0.org1.example.com'])
    parser.add_argument('-u', '--user', default='Admin@org1.example.com')
    parser.add_argument('-c', '--channel', default='channel')

    args = parser.parse_args()
    if verbose:
        print(args)
    return args

args = parse_args()

from fabric_client import FabricClient
client = FabricClient(net_profile=args.network)

# Make the client know there is a channel in the network
client.new_channel(args.channel)

username, organization = args.user.split('@')
user = client.get_user(organization, username)

n = 0

async def test_func(x, i, time_start):
    global n
    _client = copy.copy(client)
    await _client.chaincode_invoke(
        requestor=user,
        peers=args.peers,
        channel_name=args.channel,
        cc_name=CHAINCODE,  # type: string
        fcn=FUNCTION,  # type: string
        args=[
            str(x+i),
            ARG2,  # type: string
        ],
        wait_for_event=True, # for being sure chaincode invocation has been commited in the ledger, default is on tx event
    )
    n += 1
    time_elapsed = time.time() - time_start
    print(
        i+1, '/', int(args.parallelism),
        '@', time_elapsed, 'secs',
        '(', 'TPS:', n / time_elapsed, ')',
        flush=True
    )

async def main():
    x = time.time_ns()
    time_start = time.time()
    await asyncio.gather(*[test_func(x, i, time_start) for i in range(int(args.parallelism))])

loop.run_until_complete(main())
