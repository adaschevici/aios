import asyncio
import time
from aiohttp import web
from aiohttp_session import get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import threading

global_event = threading.Event()

@asyncio.coroutine
def long_running_function():
    from asyncio import sleep
    past = yield from sleep(5)
    return past

def printsy(somearg):
    print("I have done it have I not?")

@asyncio.coroutine
def handler(request):
    # session = yield from get_session(request)
    # session['last_visit'] = time.time()
    ev = threading.Event()
    result = asyncio.async(long_running_function())
    result.add_done_callback(ev.set)
    yield from asyncio.sleep(0.5)
    # result.add_done_callback(printsy)
    ev.wait()
    return web.Response(body=b'OK')

@asyncio.coroutine
def init(loop):
    app = web.Application() #middlewares=[session_middleware(
        #EncryptedCookieStorage(b'my deep dark secret'))])
    app.router.add_route('GET', '/', handler)
    srv = yield from loop.create_server(
        app.make_handler(), '0.0.0.0', 8080)
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
