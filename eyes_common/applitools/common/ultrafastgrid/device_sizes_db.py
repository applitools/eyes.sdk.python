import typing
from typing import Dict

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

    @staticmethod
    def maybe_fetch_device_sizes(server_connector):
        # type: (ServerConnector) -> None
        if not DevicesSizesDb._devices_sizes:
            DevicesSizesDb._devices_sizes.update(
                DevicesSizesDb._fetch_devices_sizes(server_connector, DeviceName)
            )
            DevicesSizesDb._devices_sizes.update(
                DevicesSizesDb._fetch_devices_sizes(server_connector, IosDeviceName)
            )

    @staticmethod
    def size(device_name, screen_orientation):
        return DevicesSizesDb._devices_sizes[device_name][screen_orientation]

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
