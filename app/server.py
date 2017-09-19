from uvicorn.run import UvicornServer
from uvicorn.protocols import http
import functools
import aiohttp_autoreload
from apistar.interfaces import App


class ReloadingServer(UvicornServer):
    async def create_server(self, loop, app, host, port):
        if getattr(app, 'debug_mode', None):
            aiohttp_autoreload.start()
        protocol = functools.partial(
            http.HttpProtocol, consumer=app, loop=loop)
        server = await loop.create_server(protocol, host=host, port=port)
        self.servers.append(server)


def run(app: App,
        host: str='127.0.0.1',
        port: int=8080,
        debug: bool=True):
    if debug:
        from uvitools.debug import DebugMiddleware
        app = DebugMiddleware(app, evalex=True)
        app.debug_mode = True

    ReloadingServer().run(app, host, port)
