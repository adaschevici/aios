import asyncio
import time
from aiohttp import web
from aiohttp_session import get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from middlewares import middleware_factory

@asyncio.coroutine
def handler(request):
    return web.Response(body=b'OK')


@asyncio.coroutine
def handler2(request):
    return web.Response(body=b"Ain't that nice but its wrong")

@asyncio.coroutine
def init(loop):
    app = web.Application(middlewares=[middleware_factory])
    app.router.add_route('GET', '/', handler)
    app.router.add_route('GET', '/run', handler2)
    srv = yield from loop.create_server(
        app.make_handler(), '0.0.0.0', 8080)
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
