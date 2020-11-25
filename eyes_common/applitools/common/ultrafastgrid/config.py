from enum import Enum
from typing import Any, Text


class ScreenOrientation(Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class DeviceName(Enum):
    iPhone_4 = "iPhone 4"
    iPhone_5SE = "iPhone 5/SE"
    iPhone_6_7_8 = "iPhone 6/7/8"
    iPhone6_7_8_Plus = "iPhone 6/7/8 Plus"
    iPhone_X = "iPhone X"
    iPad = "iPad"
    iPad_Pro = "iPad Pro"
    BlackBerry_Z30 = "BlackBerry Z30"
    Nexus_4 = "Nexus 4"
    Nexus_5 = "Nexus 5"
    Nexus_5X = "Nexus 5X"
    Nexus_6 = "Nexus 6"
    Nexus_6P = "Nexus 6P"
    Pixel_2 = "Pixel 2"
    Pixel_2_XL = "Pixel 2 XL"
    LG_Optimus_L70 = "LG Optimus L70"
    Nokia_N9 = "Nokia N9"
    Nokia_Lumia_520 = "Nokia Lumia 520"
    Microsoft_Lumia_550 = "Microsoft Lumia 550"
    Microsoft_Lumia_950 = "Microsoft Lumia 950"
    Galaxy_S3 = "Galaxy S3"
    Galaxy_S5 = "Galaxy S5"
    Kindle_Fire_HDX = "Kindle Fire HDX"
    iPad_Mini = "iPad Mini"
    Blackberry_PlayBook = "Blackberry PlayBook"
    Nexus_10 = "Nexus 10"
    Nexus_7 = "Nexus 7"
    Galaxy_Note_3 = "Galaxy Note 3"
    Galaxy_Note_2 = "Galaxy Note 2"
    Laptop_with_touch = "Laptop with touch"
    Laptop_with_HiDPI_screen = "Laptop with HiDPI screen"
    Laptop_with_MDPI_screen = "Laptop with MDPI screen"
    Pixel_3 = "Pixel 3"
    Pixel_3_XL = "Pixel 3 XL"
    Pixel_4 = "Pixel 4"
    Pixel_4_XL = "Pixel 4 XL"
    iPad_6th_Gen = "iPad 6th Gen"
    iPad_7th_Gen = "iPad 7th Gen"
    iPad_Air_2 = "iPad Air 2"
    iPhone_11 = "iPhone 11"
    iPhone_11_Pro = "iPhone 11 Pro"
    iPhone_11_Pro_Max = "iPhone 11 Pro Max"
    iPhone_XR = "iPhone XR"
    iPhone_XS = "iPhone XS"
    iPhone_XS_Max = "iPhone XS Max"
    LG_G6 = "LG G6"
    Galaxy_A5 = "Galaxy A5"
    Galaxy_Note_10 = "Galaxy Note 10"
    Galaxy_Note_10_Plus = "Galaxy Note 10 Plus"
    Galaxy_Note_4 = "Galaxy Note 4"
    Galaxy_Note_8 = "Galaxy Note 8"
    Galaxy_Note_9 = "Galaxy Note 9"
    Galaxy_S10 = "Galaxy S10"
    Galaxy_S8 = "Galaxy S8"
    Galaxy_S8_Plus = "Galaxy S8 Plus"
    Galaxy_S9_Plus = "Galaxy S9 Plus"
    Galaxy_S10_Plus = "Galaxy S10 Plus"
    Galaxy_S9 = "Galaxy S9"
    OnePlus_7T = "OnePlus 7T"
    OnePlus_7T_Pro = "OnePlus 7T Pro"


class IosVersion(Enum):
    LATEST = "latest"
    ONE_VERSION_BACK = "latest-1"


class IosDeviceName(Enum):
    iPhone_12_Pro = "iPhone 12 Pro"
    iPhone_12_Pro_Max = "iPhone 12 Pro Max"
    iPhone_12 = "iPhone 12"
    iPhone_12_mini = "iPhone 12 mini"
    iPhone_11_Pro = "iPhone 11 Pro"
    iPhone_11_Pro_Max = "iPhone 11 Pro Max"
    iPhone_11 = "iPhone 11"
    iPhone_XR = "iPhone XR"
    iPhone_XS = "iPhone Xs"
    iPhone_X = "iPhone X"
    iPhone_8 = "iPhone 8"
    iPhone_7 = "iPhone 7"
    iPad_Pro_3 = "iPad Pro (12.9-inch) (3rd generation)"
    iPad_7 = "iPad (7th generation)"
    iPad_Air_2 = "iPad Air (2nd generation)"


class VisualGridOption(object):
    def __init__(self, key, value):
        # type: (Text, Any) -> None
        self.key = key
        self.value = value
