from enum import Enum

import trafaret as trf

from applitools.common import (
    ChromeEmulationInfo,
    DesktopBrowserInfo,
    DeviceName,
    IosDeviceInfo,
    IosDeviceName,
    IosVersion,
    ProxySettings,
    RectangleSize,
    ScreenOrientation,
    StitchMode,
    VisualGridOption,
)
from applitools.common.selenium import BrowserType
from applitools.core import Feature
from applitools.selenium import BatchInfo, Configuration


class SelectedSDK(Enum):
    selenium = "selenium"
    selenium_ufg = "selenium_ufg"
    appium = "appium"


class ToEnumTrafaret(trf.Trafaret):
    def __init__(self, convert_to_enum):
        self.converter = convert_to_enum

    def check_and_return(self, value, context=None):
        return self.converter(value)


class BatchInfoTrafaret(trf.Trafaret):
    scheme = trf.Dict(
        {
            trf.Key("id", optional=True): trf.String,
            trf.Key("name", optional=True): trf.String,
            trf.Key("batch_sequence_name", optional=True): trf.String,
            trf.Key("started_at", optional=True): trf.DateTime,
            trf.Key("properties", optional=True): trf.List(
                trf.Dict(name=trf.String, value=trf.String)
            ),
        },
    )

    def check_and_return(self, value, context=None):
        sanitized = self.scheme.check(value, context=None)
        batch = BatchInfo()
        for key, val in sanitized.items():
            setattr(batch, key, val)
        return batch


class ViewPortTrafaret(trf.Trafaret):
    scheme = trf.Dict(width=trf.Int, height=trf.Int)

    def check_and_return(self, value, context=None):
        sanitized = self.scheme.check(value, context)
        return RectangleSize.from_(sanitized)


class VisualGridOptionsTrafaret(trf.Trafaret):
    scheme = trf.List(trf.Dict({"key": trf.String, "value": trf.String}))

    def check_and_return(self, value, context=None):
        sanitized = self.scheme.check(value, context)
        return [VisualGridOption(**dct) for dct in sanitized]


class DesktopBrowserInfoTrafaret(trf.Trafaret):
    scheme = trf.List(
        trf.Dict(
            {
                "browser_type": ToEnumTrafaret(BrowserType),
                "width": trf.Int,
                "height": trf.Int,
            }
        )
    )

    def check_and_return(self, value, context=None):
        sanitized = self.scheme.check(value, context)
        return [DesktopBrowserInfo(**dct) for dct in sanitized]


class IosDeviceInfoTrafaret(trf.Trafaret):
    scheme = trf.List(
        trf.Dict(
            {
                "device_name": ToEnumTrafaret(IosDeviceName),
                trf.Key("screen_orientation", optional=True): ToEnumTrafaret(
                    ScreenOrientation
                ),
                trf.Key("ios_version", optional=True): ToEnumTrafaret(IosVersion),
            }
        )
    )

    def check_and_return(self, value, context=None):
        sanitized = self.scheme.check(value, context)
        return [IosDeviceInfo(**dct) for dct in sanitized]


class ChromeEmulationInfoTrafaret(trf.Trafaret):
    scheme = trf.List(
        trf.Dict(
            {
                "device_name": ToEnumTrafaret(DeviceName),
                trf.Key("screen_orientation", optional=True): ToEnumTrafaret(
                    ScreenOrientation
                ),
            }
        )
    )

    def check_and_return(self, value, context=None):
        sanitized = self.scheme.check(value, context)
        return [ChromeEmulationInfo(**dct) for dct in sanitized]


class ProxyTrafaret(trf.Trafaret):
    scheme = trf.Dict({trf.Key("url") >> "host_or_url": trf.URL}) | trf.Dict(
        {
            trf.Key("host") >> "host_or_url": trf.String,
            "port": trf.Int,
            "username": trf.String,
            "password": trf.String,
            "scheme": trf.String,
        },
    )

    def check_and_return(self, value, context=None):
        sanitized = self.scheme.check(value, context)
        return ProxySettings(host_or_url=sanitized.pop("host_or_url"), **sanitized)


class ConfigurationTrafaret(trf.Trafaret):  # typedef
    shared_scheme = trf.Dict(
        {
            trf.Key("server_url", optional=True): trf.URL,
            trf.Key("batch", optional=True): BatchInfoTrafaret,
            trf.Key("proxy", optional=True): ProxyTrafaret,
            trf.Key("app_name", optional=True): trf.String,
            trf.Key("api_key", optional=True): trf.String,
            trf.Key("branch_name", optional=True): trf.String,
            trf.Key("parent_branch_name", optional=True): trf.String,
            trf.Key("baseline_branch_name", optional=True): trf.String,
            trf.Key("agent_id", optional=True): trf.String,
            trf.Key("baseline_env_name", optional=True): trf.String,
            trf.Key("environment_name", optional=True): trf.String,
            trf.Key("save_diffs", optional=True): trf.Bool,
            trf.Key("app_name", optional=True): trf.String,
            trf.Key("viewport_size", optional=True): ViewPortTrafaret,
            trf.Key("match_timeout", optional=True): trf.Int,
            trf.Key("save_new_tests", optional=True): trf.Bool,
            trf.Key("save_failed_tests", optional=True): trf.Bool,
            trf.Key("features", optional=True): ToEnumTrafaret(Feature),
            trf.Key("properties", optional=True): trf.List(
                trf.Dict(name=trf.String, value=trf.String)
            ),
        },
        ignore_extra="*",
    )
    selenium_scheme = trf.Dict(
        {
            trf.Key("force_full_page_screenshot", optional=True): trf.Bool,
            trf.Key("wait_before_screenshots", optional=True): trf.Int,
            trf.Key("stitch_mode", optional=True): ToEnumTrafaret(StitchMode),
            trf.Key("hide_scrollbars", optional=True): trf.Bool,
            trf.Key("hide_caret", optional=True): trf.Bool,
        },
        ignore_extra="*",
    )
    selenium_ufg_scheme = trf.Dict(
        {
            trf.Key("visual_grid_options", optional=True): VisualGridOptionsTrafaret,
            trf.Key("disable_browser_fetching", optional=True): trf.Bool,
            trf.Key("enable_cross_origin_rendering", optional=True): trf.Bool,
            trf.Key("dont_use_cookies", optional=True): trf.Bool,
            trf.Key("layout_breakpoints", optional=True): trf.Bool | trf.List(trf.Int),
            trf.Key("browsers", optional=True): trf.Dict(
                {
                    trf.Key("desktop", optional=True): DesktopBrowserInfoTrafaret,
                    trf.Key("ios", optional=True): IosDeviceInfoTrafaret,
                    trf.Key(
                        "chrome_emulation", optional=True
                    ): ChromeEmulationInfoTrafaret,
                }
            ),
        },
        ignore_extra="*",
    )
    appium_scheme = trf.Dict(
        {
            trf.Key("is_simulator", optional=True): trf.Bool,
        },
        ignore_extra="*",
    )
    scheme = shared_scheme + selenium_scheme + selenium_ufg_scheme + appium_scheme

    def check_and_return(self, value, context=None):
        sanitized = self.scheme.check(value, context)
        conf = Configuration()
        for key, val in sanitized.items():
            setattr(conf, key, val)
        return conf
