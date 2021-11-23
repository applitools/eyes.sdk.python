import atexit
import weakref
from concurrent.futures import Future
from itertools import count
from json import dumps, loads
from threading import Thread
from typing import Optional, Text

from websocket import WebSocket

from applitools.eyes_server import get_instance, server

_all_sockets = []


class USDKConnection(object):
    def __init__(self, websocket, server_log_file=None):
        # type: (WebSocket, Optional[Text]) -> None
        self.server_log_file = server_log_file
        self._websocket = websocket
        self._keys = count(1)
        self._response_futures = {}
        weak_socket = weakref.ref(self._websocket)
        self._receiver_thread = Thread(
            target=self._receiver_loop,
            name="USDK Receiver",
            args=(weak_socket, self._response_futures),
        )
        # Receiver threads are designed to exit even if they serve leaked unclosed
        # connections. But non-daemon threads are joined on shutdown deadlocking with
        # garbage collector and atexit manager that should close the socket
        self._receiver_thread.daemon = True
        _all_sockets.append(weak_socket)
        self._receiver_thread.start()

    @classmethod
    def create(cls, server=None):
        # type: (Optional[server.SDKServer]) -> USDKConnection
        server = server or get_instance()
        websocket = WebSocket()
        websocket.connect("ws://localhost:{}/eyes".format(server.port))
        websocket.settimeout(3 * 60)
        return cls(websocket, server.log_file_name)

    def notification(self, name, payload):
        # type: (Text, dict) -> None
        self._websocket.send(dumps({"name": name, "payload": payload}))

    def command(self, name, payload):
        # type: (Text, dict) -> dict
        key = next(self._keys)
        future = Future()
        self._response_futures[key] = future
        self._websocket.send(dumps({"name": name, "key": key, "payload": payload}))
        return future.result(3 * 60)

    def set_timeout(self, timeout):
        # type: (Optional[float]) -> None
        self._websocket.settimeout(timeout)

    def close(self):
        if self._websocket:
            self._websocket.close()
            self._websocket = None
            self._receiver_thread = None

    def __del__(self):
        self.close()

    @staticmethod
    def _receiver_loop(weak_socket, response_futures):
        while True:
            try:
                socket = weak_socket()
                if not socket:
                    raise EOFError
                response = socket.recv()
                del socket
                if not response:
                    raise EOFError
                response = loads(response)
                future = response_futures.pop(response["key"])
                future.set_result(response)
            except Exception as exc:
                for future in response_futures.values():
                    future.set_exception(exc)
                break


@atexit.register
def ensure_all_closed():
    for weak_ref in _all_sockets:
        socket = weak_ref()
        if socket:
            socket.close()