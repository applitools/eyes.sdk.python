import atexit
import logging
import weakref
from concurrent.futures import Future
from json import dumps, loads
from threading import Thread
from typing import Optional, Text
from uuid import uuid1

from websocket import WebSocket

from applitools.eyes_universal import get_instance

_all_sockets = []
_logger = logging.getLogger(__name__)


class USDKConnection(object):
    def __init__(self, websocket):
        # type: (WebSocket) -> None
        self._websocket = websocket
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
        return cls(websocket)

    def notification(self, name, payload):
        # type: (Text, dict) -> None
        self._websocket.send(dumps({"name": name, "payload": payload}))

    def command(self, name, payload, wait_result, wait_timeout):
        # type: (Text, dict, bool, float) -> Optional[dict]
        key = str(uuid1())
        future = Future()
        self._response_futures[key] = future
        self._websocket.send(dumps({"name": name, "key": key, "payload": payload}))
        if wait_result:
            return future.result(wait_timeout)
        else:
            return None

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
                if "key" in response:
                    future = response_futures.pop(response["key"])
                    future.set_result(response)
                elif response.get("name") == "Server.log":
                    entry = response["payload"]
                    level = logging.getLevelName(entry["level"].upper())
                    _logger.log(level, entry["message"])
                else:
                    _logger.warning("Unexpected server-initiated event %s", response)
            except Exception as exc:
                socket = weak_socket()
                if socket:
                    socket.abort()
                for future in response_futures.values():
                    future.set_exception(exc)
                break


@atexit.register
def ensure_all_closed():
    for weak_ref in _all_sockets:
        socket = weak_ref()
        if socket:
            socket.close()
