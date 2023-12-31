# Modules
import asyncio
import os
import random
import socket
import struct

from pynput.keyboard import Controller, Key

from PyRTMPHelper import SimpleServer


def randomHost() -> str:
    return "127.0.0.1"  # socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))


async def stopEverything(fun):
    value = input("")

    while value != "c":
        value = input("")

    if value == "c":
        await fun()
        # exit()


class SetupServer:

    def __init__(self, directory: str, streamsURLs: str):
        self.directory = directory
        self.streams = streamsURLs
        self.server = self.createServer()

    def createServer(self) -> SimpleServer:
        server = SimpleServer(output_directory=self.directory, streams=self.streams)
        return server

    async def startServer(self):
        await self.server.create(host=randomHost(), port=(1935 + random.randint(0, 2)))
        await self.server.start()
        await stopEverything(self.server.stop())

    async def stopServer(self):
        await self.server.stop()


async def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    streams = ("\"[f=flv:onfail=ignore]rtmp://live.twitch.tv/app/live_52418627_JzRSvB5D0OF5SZMLqUZEdo4ruEi0sT|"
               "[f=flv:onfail=ignore]rtmp://a.rtmp.youtube.com/live2/k1au-gehy-0fu1-fjp3-a11x\"")
    server = SetupServer(current_dir, streams)
    await server.startServer()


if __name__ == "__main__":
    asyncio.run(main())
