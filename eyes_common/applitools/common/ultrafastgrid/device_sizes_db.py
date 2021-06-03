import typing
from typing import Dict, Optional

from applitools.common.geometry import RectangleSize
from applitools.common.ultrafastgrid.config import (
    DeviceName,
    IosDeviceName,
    ScreenOrientation,
)

if typing.TYPE_CHECKING:
    from applitools.core import ServerConnector


class DevicesSizesDb(object):
    _devices_sizes = {}  # type: Dict[type, Dict[ScreenOrientation, RectangleSize]]
    _server_connector = None  # type: Optional[ServerConnector]

    @staticmethod
    def maybe_set_server_connector(server_connector):
        if not DevicesSizesDb._devices_sizes and not DevicesSizesDb._server_connector:
            DevicesSizesDb._server_connector = server_connector

    @staticmethod
    def size(device_name, screen_orientation):
        DevicesSizesDb._maybe_fetch_device_sizes()
        return DevicesSizesDb._devices_sizes[device_name][screen_orientation]

    @staticmethod
    def _maybe_fetch_device_sizes():
        if not DevicesSizesDb._devices_sizes:
            server_connector = DevicesSizesDb._server_connector
            DevicesSizesDb._devices_sizes.update(
                DevicesSizesDb._fetch_devices_sizes(server_connector, DeviceName)
            )
            DevicesSizesDb._devices_sizes.update(
                DevicesSizesDb._fetch_devices_sizes(server_connector, IosDeviceName)
            )
            DevicesSizesDb._server_connector = None

    @staticmethod
    def _fetch_devices_sizes(server_connector, device_type):
        sizes = server_connector.get_devices_sizes(device_type)
        return {
            device: {
                orientation: RectangleSize.from_(sizes[device.value][orientation.value])
                for orientation in ScreenOrientation
            }
            for device in device_type
        }
