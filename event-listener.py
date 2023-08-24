import argparse
import asyncio
import ast
import asyncio
import os
import signal

from pprint import pprint

from hfc.fabric import Client


loop = asyncio.get_event_loop()


def parse_args(verbose=True):
    executable = f'python {os.path.basename(__file__)}'
    parser = argparse.ArgumentParser(
        prog = executable,
        description = 'A tool for listening events on Fabric network (1.4.x)',
        epilog = f'{executable}'
    )

    parser.add_argument('-s', '--settings', default=os.getenv('SETTINGS_DEFAULT') or 'settings/config-local.json')
    parser.add_argument('-p', '--peers', nargs='+', default=['peer0.org1.example.com'])
    parser.add_argument('-u', '--user')
    parser.add_argument('-c', '--channel', default='channel')

    parser.add_argument('-cc', '--chaincode')

    args = parser.parse_args()

    if not args.user:
        args.user = f"Admin@{args.peers[0].split('.', 1)[1]}"

    if verbose:
        print(args)

    return args


args = parse_args()


class AsyncClass:

    @classmethod
    async def create(cls, *args, **kwargs):
        self = EventHandler(*args, **kwargs)
        await self.setup(*args, **kwargs)

    async def setup(self, *args, **kwargs):
        pass


class EventHandler(AsyncClass):

    def __init__(self, settings, peers, user, channel, **kwargs):
        self.client = Client(net_profile=settings)

        self.peers = [self.client.get_peer(x) for x in peers]

        username, organization = user.split('@')
        self.user = self.client.get_user(organization, username)

        self.channel_name = channel
        # Make the client know there is a channel in the network
        self.channel = self.client.new_channel(self.channel_name)

    async def setup(self, *args, **kwargs):
        pass

    async def get_height(self):
        info = await self.client.query_info(self.user, self.channel_name, self.peers)
        return info.height

    async def listen_for_events(self):
        channel_event_hub = self.channel.newChannelEventHub(self.peers[0], self.user)
        # registerChaincodeEvent(self, ccid, pattern, unregister=False, start=None, stop=None, as_array=None, disconnect=False, onEvent=None)
        channel_event_hub.registerChaincodeEvent(args.chaincode, '.*', onEvent=self.onEvent)
        height = await self.get_height()
        stream = channel_event_hub.connect(filtered=False, start=height)
        await stream
        channel_event_hub.disconnect()

    def onEvent(self, event, block_num, tx_id, tx_status):
        self.event_handler(event)

    def event_handler(self, event):
        print(event)


class EventLogger(EventHandler):

    def event_handler(self, event):
        event['data'] = ast.literal_eval(event['payload'].decode("UTF-8"))
        print('')  # newline
        pprint(event)
        print('')  # newline


event_handler = EventLogger(**vars(args))


async def main():
    #await event_handler.setup()
    print('Ready! (Tap Ctrl-C twice to exit.)')
    await event_handler.listen_for_events()


def sigint_handler(*args):
    print('\nBye!')
    exit()


signal.signal(signal.SIGINT, sigint_handler)
loop.run_until_complete(main())
