import typing
from threading import Lock
from typing import Dict, Optional

from applitools.common.geometry import RectangleSize
from applitools.common.ultrafastgrid.config import (
    DeviceName,
    IosDeviceName,
    ScreenOrientation,
)

if typing.TYPE_CHECKING:
    from applitools.core import ServerConnector


_lock = Lock()
_devices_sizes = {}  # type: Dict[type, Dict[ScreenOrientation, RectangleSize]]
_server_connector = None  # type: Optional[ServerConnector]


def maybe_set_server_connector(server_connector):
    with _lock:
        global _server_connector
        if not _devices_sizes and not _server_connector:
            _server_connector = server_connector


def size(device_name, screen_orientation):
    _maybe_fetch_device_sizes()
    return _devices_sizes[device_name][screen_orientation]


def _maybe_fetch_device_sizes():
    with _lock:
        if not _devices_sizes:
            global _server_connector
            for dev_type in DeviceName, IosDeviceName:
                _devices_sizes.update(_fetch_devices_sizes(dev_type))
            _server_connector = None


def _fetch_devices_sizes(device_type):
    sizes = _server_connector.get_devices_sizes(device_type)
    return {
        device: {
            orientation: RectangleSize.from_(sizes[device.value][orientation.value])
            for orientation in ScreenOrientation
        }
        for device in device_type
    }
