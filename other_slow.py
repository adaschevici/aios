import aiohttp.server
import asyncio
import time
from concurrent.futures import ProcessPoolExecutor

def slow_func():
  time.sleep(10)
  return "test"

class HttpProtocol(aiohttp.server.ServerHttpProtocol):

    def __init__(self, loop, ppexecutor):
        super(HttpProtocol, self).__init__(loop=loop, debug=True)
        self.loop = loop
        self.ppexecutor = ppexecutor
        #print(ppexecutor)

    async def handle_request(self, message, payload):
# ppexecutor is a ProcessPoolExecutor instance
        print('Handle request', message)
        data = await self.loop.run_in_executor(None, slow_func)
        response = aiohttp.Response(self.writer, 200, http_version=message.version, close=True)

        response.add_headers(
          ('Content-Type', 'text'),
          ('Content-Length', str(len(data)))
        )
        response.send_headers()
        response.write(data.encode())
        response.write_eof()
        self.keep_alive(False)

def main():
    pp = ProcessPoolExecutor(3)
    loop = asyncio.get_event_loop()
    myserver =  HttpProtocol(loop=loop, ppexecutor=pp)
    f = loop.create_server(
            myserver, '127.0.0.1', 8080)
    svr = loop.run_until_complete(f)
    socks = svr.sockets
    print('serving on', socks[0].getsockname())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
