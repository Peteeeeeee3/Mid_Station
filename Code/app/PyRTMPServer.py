# Modules
import asyncio
import os

from PyRTMPHelper import SimpleServer


def _setupStreams(streams: str) -> str:
    urls = streams.split(',')
    i = 1
    ffmpeg = ""
    for url in urls:
        if i == 1:
            ffmpeg = ffmpeg + "\"" + "[f=flv:onfail=ignore]" + url + "|"
        elif i <= len(urls):
            ffmpeg = ffmpeg + "[f=flv:onfail=ignore]" + url + "|"
        i = i + 1
    return ffmpeg


class SetupServer:

    def __init__(self, streamsURLs: str, ipAddress: str):
        self.streams = _setupStreams(streamsURLs)
        self.ipaddress = ipAddress
        self.server = self._createServer()

    def _createServer(self) -> SimpleServer:
        server = SimpleServer(os.path.dirname(os.path.abspath(__file__)), streams=self.streams)
        return server

    async def _startServer(self):
        await self.server.create(self.ipaddress, port=1935)
        await self.server.start()
        await self.server.wait_closed()

    def GoLive(self):
        asyncio.run(self._startServer())

    async def StopLive(self):
        await self.server.stop()
