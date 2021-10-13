from itertools import count
from json import dumps, loads
from typing import Optional, Text
from uuid import uuid4

from websocket import WebSocket


class USDKConnection(object):
    def __init__(self, websocket):
        # type: (WebSocket) -> None
        self._websocket = websocket

    @classmethod
    def create(cls, port=2107):
        # type: (int) -> USDKConnection
        websocket = WebSocket()
        websocket.connect("ws://localhost:{}/eyes".format(port))
        return cls(websocket)

    def notification(self, name, payload):
        # type: (Text, dict) -> None
        self._websocket.send(dumps({"name": name, "payload": payload}))

    def command(self, name, payload):
        # type: (Text, dict) -> dict
        key = str(uuid4())
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
