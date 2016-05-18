import aiohttp.server
import asyncio
import time


def slow_func():
  time.sleep(5)
  return "test"


class HttpProtocol(aiohttp.server.ServerHttpProtocol):

  async def handle_request(self, message, payload):
      print('Handle request', message)
      data =  await asyncio.get_event_loop().run_in_executor(
          None, slow_func)

      response = aiohttp.Response(
          self.writer, 200, http_version=message.version, close=True)

      response.add_headers(
          ('Content-Type', 'text'),
          ('Content-Length', str(len(data)))
      )
      response.send_headers()
      response.write(data.encode())
      response.write_eof()
      self.keep_alive(False)


def main():
    loop = asyncio.get_event_loop()
    f = loop.create_server(
        lambda: HttpProtocol(debug=True), '127.0.0.1', 8080)
    svr = loop.run_until_complete(f)
    socks = svr.sockets
    print('serving on', socks[0].getsockname())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
