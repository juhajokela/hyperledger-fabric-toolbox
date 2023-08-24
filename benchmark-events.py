import argparse
import asyncio
import ast
import os
import time

loop = asyncio.get_event_loop()

def parse_args(verbose=True):
    executable = f'python {os.path.basename(__file__)}'
    parser = argparse.ArgumentParser(
        prog = executable,
        description = 'A tool for benchmarking chaincode on Fabric network (1.4.x)',
        epilog = f'{executable} invoke CHAINCODE FUNCTION ARG1 ARG2 ... | {executable} query CHAINCODE FUNCTION ARG1 ...'
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

from hfc.fabric import Client
client = Client(net_profile=args.network)

# Make the client know there is a channel in the network
client.new_channel(args.channel)

username, organization = args.user.split('@')
user = client.get_user(organization, username)


events = {}


class EventHandler:

    def __init__(self, network, peers, user, channel):
        self.client = Client(net_profile=network)

        self.peers = [self.client.get_peer(x) for x in peers]

        username, organization = user.split('@')
        self.user = self.client.get_user(organization, username)

        self.channel_name = channel
        # Make the client know there is a channel in the network
        self.channel = self.client.new_channel(self.channel_name)

    async def get_height(self):
        info = await self.client.query_info(self.user, self.channel_name, self.peers)
        return info.height

    async def listen_for_events(self):
        self.channel_event_hub = self.channel.newChannelEventHub(self.peers[0], self.user)
        # registerChaincodeEvent(self, ccid, pattern, unregister=False, start=None, stop=None, as_array=None, disconnect=False, onEvent=None)
        self.channel_event_hub.registerChaincodeEvent(CHAINCODE, '.*', onEvent=self.onEvent)
        height = await self.get_height()
        stream = self.channel_event_hub.connect(filtered=False, start=height)
        await stream

    def stop(self):
        self.channel_event_hub.disconnect()

    def onEvent(self, event, block_num, tx_id, tx_status):
        self.event_handler(event)

    def event_handler(self, event):
        from pprint import pprint
        event['data'] = ast.literal_eval(event['payload'].decode("UTF-8"))
        print('')  # newline
        pprint(event)
        print('')  # newline


event_handler = EventHandler(
    args.network, args.peers, args.user, args.channel
)

async def test_func(x, i, time_start):
    print('*', await client.chaincode_invoke(
        requestor=user,
        channel_name=args.channel,
        peers=args.peers,
        fcn=FUNCTION,  # type: string
        args=[str(x+i), ARG2, ...],
        cc_name=CHAINCODE,  # type: string
        wait_for_event=False, # for being sure chaincode invocation has been commited in the ledger, default is on tx event
        #cc_pattern='^invoked*' # if you want to wait for chaincode event and you have a `stub.SetEvent("invoked", value)` in your chaincode
    ))

    time_elapsed = time.time() - time_start
    print(i+1, '/', int(args.parallelism), '@', time_elapsed, 'secs',  flush=True)

async def main():
    print('\n---\n')

    event_listener = asyncio.create_task(event_handler.listen_for_events())

    x = time.time_ns()
    time_start = time.time()
    await asyncio.gather(*[test_func(x, i, time_start) for i in range(int(args.parallelism))])
    time_elapsed = time.time() - time_start
    print('time elapsed:', time_elapsed, 'TPS:', int(args.parallelism)/time_elapsed, flush=True)
    event_handler.stop()

loop.run_until_complete(main())