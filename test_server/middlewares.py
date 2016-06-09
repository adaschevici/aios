import asyncio
from aiohttp import web

@asyncio.coroutine
def middleware_factory(app, handler):
    @asyncio.coroutine
    def middleware_handler(request):
        if request.path.endswith("/run"):
            return web.Response(status=403, body=b'you are not allowed to pass')
        return (yield from handler(request))
    return middleware_handler
