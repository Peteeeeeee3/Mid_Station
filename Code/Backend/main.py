# Modules
import asyncio
import os
import logging
from asyncio import StreamReader

from pyrtmp import StreamClosedException
from pyrtmp.session_manager import SessionManager
from pyrtmp.flv import FLVWriter, FLVMediaType
from pyrtmp.rtmp import SimpleRTMPController, RTMPProtocol, SimpleRTMPServer

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class RTMP2SocketController(SimpleRTMPController):

    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        super().__init__()

    async def on_ns_publish(self, session, message) -> None:
        publishing_name = message.publishing_name
        prefix = os.path.join(self.output_directory, f'{publishing_name}')
        session.state = RemoteProcessFLVWriter()
        logger.debug(f'output to {prefix}.flv')
        await session.state.initialize(
            command=f"ffmpeg -y -i pipe:0 -map 0 -c:v copy -c:a copy -b:v 1000k -maxrate 1000k -bufsize 2000k -g 50 "
                    f"-flags +global_header -f tee"
                    f"\"[f=flv:onfail=ignore]rtmp://live.twitch.tv/app/|"
                    f"[f=flv:onfail=ignore]rtmp://a.rtmp.youtube.com/live2/\"",
            stdout_log=f'{prefix}.stdout.log',
            stderr_log=f'{prefix}.stderr.log',
        )
        session.state.write_header()
        await super().on_ns_publish(session, message)

    async def on_metadata(self, session, message) -> None:
        session.state.write(0, message.to_raw_meta(), FLVMediaType.OBJECT)
        await super().on_metadata(session, message)

    async def on_video_message(self, session, message) -> None:
        session.state.write(message.timestamp, message.payload, FLVMediaType.VIDEO)
        await super().on_video_message(session, message)

    async def on_audio_message(self, session, message) -> None:
        session.state.write(message.timestamp, message.payload, FLVMediaType.AUDIO)
        await super().on_audio_message(session, message)

    async def on_stream_closed(self, session: SessionManager, exception: StreamClosedException) -> None:
        await session.state.close()
        await super().on_stream_closed(session, exception)


class RemoteProcessFLVWriter:

    def __init__(self):
        self.proc = None
        self.stdout = None
        self.stderr = None
        self.writer = FLVWriter()

    async def initialize(self, command: str, stdout_log: str, stderr_log: str):
        self.proc = await asyncio.create_subprocess_shell(
            command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        self.stdout = asyncio.create_task(self._read_to_file(stdout_log, self.proc.stdout))
        self.stderr = asyncio.create_task(self._read_to_file(stderr_log, self.proc.stderr))

    async def _read_to_file(self, filename: str, stream: StreamReader):
        fp = open(filename, 'wt')
        while not stream.at_eof():
            data = await stream.readline()
            fp.write(data.decode())
            fp.flush()
        fp.close()

    def write_header(self):
        buffer = self.writer.write_header()
        self.proc.stdin.write(buffer)

    def write(self, timestamp: int, payload: bytes, media_type: FLVMediaType):
        buffer = self.writer.write(timestamp, payload, media_type)
        self.proc.stdin.write(buffer)

    async def close(self):
        await self.proc.stdin.drain()
        self.proc.stdin.close()
        await self.proc.wait()


class SimpleServer(SimpleRTMPServer):

    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        super().__init__()

    async def create(self, host: str, port: int):
        loop = asyncio.get_event_loop()
        self.server = await loop.create_server(
            lambda: RTMPProtocol(controller=RTMP2SocketController(self.output_directory)),
            host=host,
            port=port,
        )


async def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server = SimpleServer(output_directory=current_dir)
    await server.create(host='127.0.0.1', port=1935)
    await server.start()
    await server.wait_closed()


# Main Function
if __name__ == '__main__':
    asyncio.run(main())