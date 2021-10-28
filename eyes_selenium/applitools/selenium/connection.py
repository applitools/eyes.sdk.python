import sys
import weakref
from concurrent.futures import Future
from itertools import count
from json import dumps, loads
from threading import Thread
from typing import Optional, Text

from websocket import WebSocket


class USDKConnection(object):
    def __init__(self, websocket):
        # type: (WebSocket) -> None
        self._websocket = websocket
        self._keys = count(1)

    @classmethod
    def create(cls, port=2107):
        # type: (int) -> USDKConnection
        websocket = WebSocket()
        websocket.connect("ws://localhost:{}/eyes".format(port))
        websocket.settimeout(3 * 60)
        return cls(websocket)

    def notification(self, name, payload):
        # type: (Text, dict) -> None
        self._websocket.send(dumps({"name": name, "payload": payload}))

    def command(self, name, payload):
        # type: (Text, dict) -> dict
        key = next(self._keys)
        self._websocket.send(dumps({"name": name, "key": key, "payload": payload}))
        response = loads(self._websocket.recv())
        assert response["name"] == name and response["key"] == key
        return response

    def set_timeout(self, timeout):
        # type: (Optional[float]) -> None
        self._websocket.settimeout(timeout)

    def close(self):
        self._websocket.close()
        self._websocket = None


class USDKSharedConnection(object):
    def __init__(self, websocket):
        # type: (WebSocket) -> None
        self._websocket = websocket
        self._keys = count(1)
        self._response_futures = {}
        self._receiver_thread = Thread(
            target=self._receiver_loop,
            name="USDK Receiver",
            args=(weakref.ref(self._websocket), self._response_futures),
        )
        self._receiver_thread.start()

    @classmethod
    def create(cls, port=2107):
        # type: (int) -> USDKConnection
        websocket = WebSocket(enable_multithread=True)
        websocket.connect("ws://localhost:{}/eyes".format(port))
        websocket.settimeout(9 * 60)
        return cls(websocket)

    def notification(self, name, payload):
        # type: (Text, dict) -> None
        self._websocket.send(dumps({"name": name, "payload": payload}))

    def command(self, name, payload):
        # type: (Text, dict) -> dict
        key = next(self._keys)
        future = Future()
        self._response_futures[key] = future
        self._websocket.send(dumps({"name": name, "key": key, "payload": payload}))
        return future.result(9 * 60)

    def set_timeout(self, timeout):
        # type: (Optional[float]) -> None
        self._websocket.settimeout(timeout)

    def close(self):
        self._websocket.close()
        self._websocket = None
        self._receiver_thread.join()
        self._receiver_thread = None

    def __del__(self):
        if self._websocket:
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
