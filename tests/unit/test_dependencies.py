import cattr

from applitools.common import AndroidDeviceInfo, AndroidDeviceName


def test_cattrs_non_enum_unstructur():
    android_device_info = AndroidDeviceInfo(AndroidDeviceName.Pixel_4_XL)

    unstructured = cattr.unstructure(android_device_info)

    assert unstructured == {
        "android_version": None,
        "device_name": "Pixel 4 XL",
        "screen_orientation": None,
    }
