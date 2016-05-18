from aiohttp import web
import asyncio
from concurrent.futures import ProcessPoolExecutor


class Upper(web.Application):

    def __init__(self, loop, ppool):
        print("Building")
        web.Application.__init__(self)
        self.pool = loop
        self.ppool = ppool
        print("Ended building")

    async def some_handler(self, request):
        from ipdb import set_trace; set_trace()
        return web.Response(body=str("Hello World").encode("utf-8"), status=200)

def main():
    pp = ProcessPoolExecutor(4)
    loop = asyncio.get_event_loop()
    app = Upper(loop=loop, ppool=pp)
    app.router.add_route("GET", "/", app.some_handler)
    f = loop.create_server(app.make_handler(),
            "127.0.0.1", 8080)
    loop.run_until_complete(f)
    try:
        loop.run_forever()
    except:
        pass

if __name__=="__main__":
    main()
