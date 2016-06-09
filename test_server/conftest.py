import cgi
import contextlib
import gc
import email.parser
import functools
import http.server
import json
import logging
import io
import os
import re
import socket
import ssl
import sys
import threading
import traceback
import urllib.parse
import unittest

import asyncio
import aiohttp
import asyncio
import aiohttp
import collections
import logging
import pytest
import warnings
import socket
import contextlib
from aiohttp import web




@contextlib.contextmanager
def loop_context():
    """a contextmanager that creates an event_loop, for test purposes.
    handles the creation and cleanup of a test loop.
    """
    loop = setup_test_loop()
    yield loop
    teardown_test_loop(loop)


def setup_test_loop():
    """create and return an asyncio.BaseEventLoop
    instance. The caller should also call teardown_test_loop,
    once they are done with the loop.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)
    return loop


def teardown_test_loop(loop):
    """teardown and cleanup an event_loop created
    by setup_test_loop.
    :param loop: the loop to teardown
    :type loop: asyncio.BaseEventLoop
    """
    is_closed = getattr(loop, 'is_closed')
    if is_closed is not None:
        closed = is_closed()
    else:
        closed = loop._closed
    if not closed:
        loop.call_soon(loop.stop)
        loop.run_forever()
        loop.close()
    gc.collect()
    asyncio.set_event_loop(None)

class Client:
    def __init__(self, session, url):
        self._session = session
        if not url.endswith('/'):
            url += '/'
        self._url = url

    def close(self):
        self._session.close()

    def get(self, path, **kwargs):
        while path.startswith('/'):
            path = path[1:]
        url = self._url + path
        return self._session.get(url, **kwargs)

    def post(self, path, **kwargs):
        while path.startswith('/'):
            path = path[1:]
        url = self._url + path
        return self._session.post(url, **kwargs)

    def delete(self, path, **kwargs):
        while path.startswith('/'):
            path = path[1:]
        url = self._url + path
        return self._session.delete(url)

    def ws_connect(self, path, **kwargs):
        while path.startswith('/'):
            path = path[1:]
        url = self._url + path
        return self._session.ws_connect(url, **kwargs)


@pytest.yield_fixture
def loop():
    with loop_context() as loop:
        yield loop

def unused_port():
    """ return a port that is unused on the current host. """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

pytest.fixture(unused_port)

@pytest.yield_fixture
def create_server(loop):
    app = handler = srv = None

    @asyncio.coroutine
    def create(*, debug=False, ssl_ctx=None, proto='http'):
        nonlocal app, handler, srv
        app = web.Application(loop=loop)
        port = unused_port()
        handler = app.make_handler(debug=debug, keep_alive_on=False)
        srv = yield from loop.create_server(handler, '127.0.0.1', port,
                                            ssl=ssl_ctx)
        if ssl_ctx:
            proto += 's'
        url = "{}://127.0.0.1:{}".format(proto, port)
        return app, url

    yield create


    @asyncio.coroutine
    def finish():
        yield from handler.finish_connections()
        yield from app.finish()
        srv.close()
        yield from srv.wait_closed()

    loop.run_until_complete(finish())

@pytest.yield_fixture
def create_app_and_client(create_server, loop):
    client = None

    @asyncio.coroutine
    def maker(*, server_params=None, client_params=None):
        nonlocal client
        if server_params is None:
            server_params = {}
        server_params.setdefault('debug', False)
        server_params.setdefault('ssl_ctx', None)
        app, url = yield from create_server(**server_params)
        if client_params is None:
            client_params = {}
        client = Client(aiohttp.ClientSession(loop=loop, **client_params), url)
        return app, client

    yield maker
    client.close()

@pytest.mark.tryfirst
def pytest_pycollect_makeitem(collector, name, obj):
    if collector.funcnamefilter(name):
        if not callable(obj):
            return
        item = pytest.Function(name, parent=collector)
        if 'run_loop' in item.keywords:
            return list(collector._genfunctions(name, obj))


@pytest.mark.tryfirst
def pytest_pyfunc_call(pyfuncitem):
    """
    Run asyncio marked test functions in an event loop instead of a normal
    function call.
    """
    if 'run_loop' in pyfuncitem.keywords:
        funcargs = pyfuncitem.funcargs
        loop = funcargs['loop']
        testargs = {arg: funcargs[arg]
                    for arg in pyfuncitem._fixtureinfo.argnames}
        loop.run_until_complete(pyfuncitem.obj(**testargs))
        return True


def pytest_runtest_setup(item):
    if 'run_loop' in item.keywords and 'loop' not in item.fixturenames:
        # inject an event loop fixture for all async tests
        item.fixturenames.append('loop')


# def pytest_ignore_collect(path, config):
#     if 'test_py35' in str(path):
#         if sys.version_info < (3, 5, 0):
#             return True
# 
