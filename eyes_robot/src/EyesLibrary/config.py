import trafaret as t

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


def _enum_to_list_of_values(enum):
    return [e.value for e in enum]


class BatchInfoTrafaret(t.Trafaret):
    scheme = t.Dict(
        {
            t.Key("id", optional=True): t.String,
            t.Key("name", optional=True): t.String,
            t.Key("batch_sequence_name", optional=True): t.String,
            t.Key("started_at", optional=True): t.DateTime,
        },
    )

    def check(self, value, context=None):
        sanitized = self.scheme.check(value, context=None)
        batch = BatchInfo()
        for key, val in sanitized.items():
            setattr(batch, key, val)
        return batch


class ViewPortTrafaret(t.Trafaret):
    scheme = t.Dict(width=t.Int, height=t.Int)

    def check(self, value, context=None):
        sanitized = self.scheme.check(value, context)
        return RectangleSize.from_(sanitized)


class VisualGridOptionsTrafaret(t.Trafaret):
    scheme = t.List(t.Dict({"key": t.String, "value": t.String}))

    def check(self, value, context=None):
        sanitized = self.scheme.check(value, context)
        return [VisualGridOption(**dct) for dct in sanitized]


class DesktopBrowserInfoTrafaret(t.Trafaret):
    scheme = t.List(
        t.Dict(
            {
                "browser_type": t.Enum(*_enum_to_list_of_values(BrowserType)),
                "width": t.Int,
                "height": t.Int,
            }
        )
    )

    def check(self, value, context=None):
        sanitized = self.scheme.check(value, context)
        return [DesktopBrowserInfo(**dct) for dct in sanitized]


class IosDeviceInfoTrafaret(t.Trafaret):
    scheme = t.List(
        t.Dict(
            {
                "device_name": t.Enum(*_enum_to_list_of_values(IosDeviceName)),
                t.Key("screen_orientation", optional=True): t.Enum(
                    *_enum_to_list_of_values(ScreenOrientation)
                ),
                t.Key("ios_version", optional=True): t.Enum(
                    *_enum_to_list_of_values(IosVersion)
                ),
            }
        )
    )

    def check(self, value, context=None):
        sanitized = self.scheme.check(value, context)
        return [IosDeviceInfo(**dct) for dct in sanitized]


class ChromeEmulationInfoTrafaret(t.Trafaret):
    scheme = t.List(
        t.Dict(
            {
                "device_name": t.Enum(*_enum_to_list_of_values(DeviceName)),
                t.Key("screen_orientation", optional=True): t.Enum(
                    *_enum_to_list_of_values(ScreenOrientation)
                ),
            }
        )
    )

    def check(self, value, context=None):
        sanitized = self.scheme.check(value, context)
        return [ChromeEmulationInfo(**dct) for dct in sanitized]


class ProxyTrafaret(t.Trafaret):
    scheme = t.Dict({t.Key("url") >> "host_or_url": t.URL}) | t.Dict(
        {
            t.Key("host") >> "host_or_url": t.String,
            "port": t.Int,
            "username": t.String,
            "password": t.String,
            "scheme": t.String,
        },
    )

    def check(self, value, context=None):
        sanitized = self.scheme.check(value, context)
        return ProxySettings(host_or_url=sanitized.pop("host_or_url"), **sanitized)


def sanitize_raw_config(raw_config):
    # type: (dict) -> dict
    config_scheme = t.Dict(
        {
            t.Key("server_url", optional=True): t.URL,
            t.Key("batch", optional=True): BatchInfoTrafaret,
            t.Key("proxy", optional=True): ProxyTrafaret,
            t.Key("app_name", optional=True): t.String,
            t.Key("api_key", optional=True): t.String,
            t.Key("branch_name", optional=True): t.String,
            t.Key("parent_branch_name", optional=True): t.String,
            t.Key("baseline_branch_name", optional=True): t.String,
            t.Key("agent_id", optional=True): t.String,
            t.Key("baseline_env_name", optional=True): t.String,
            t.Key("environment_name", optional=True): t.String,
            t.Key("save_diffs", optional=True): t.Bool,
            t.Key("app_name", optional=True): t.String,
            t.Key("viewport_size", optional=True): ViewPortTrafaret,
            t.Key("match_timeout", optional=True): t.Int,
            t.Key("save_new_tests", optional=True): t.Bool,
            t.Key("save_failed_tests", optional=True): t.Bool,
            t.Key("features", optional=True): t.Enum(*_enum_to_list_of_values(Feature)),
            t.Key("eyes_selenium", optional=True): t.Dict(
                {
                    t.Key("force_full_page_screenshot", optional=True): t.Bool,
                    t.Key("wait_before_screenshots", optional=True): t.Int,
                    t.Key("stitch_mode", optional=True): t.Enum(
                        *_enum_to_list_of_values(StitchMode)
                    ),
                    t.Key("hide_scrollbars", optional=True): t.Bool,
                    t.Key("hide_caret", optional=True): t.Bool,
                },
                allow_extra="*",
            ),
            t.Key("eyes_appium", optional=True): t.Dict(
                {
                    t.Key("is_simulator", optional=True): t.Bool,
                },
                allow_extra="*",
            ),
            t.Key("eyes_selenium_ufg", optional=True): t.Dict(
                {
                    t.Key(
                        "visual_grid_options", optional=True
                    ): VisualGridOptionsTrafaret,
                    t.Key("disable_browser_fetching", optional=True): t.Bool,
                    t.Key("enable_cross_origin_rendering", optional=True): t.Bool,
                    t.Key("dont_use_cookies", optional=True): t.Bool,
                    t.Key("layout_breakpoints", optional=True): t.Bool | t.List(t.Int),
                    t.Key(
                        "chrome_emulatoin_devices", optional=True
                    ): ChromeEmulationInfoTrafaret,
                    t.Key("ios_devices", optional=True): IosDeviceInfoTrafaret,
                    t.Key("browsers", optional=True): DesktopBrowserInfoTrafaret,
                },
                allow_extra="*",
            ),
        },
        allow_extra="*",
    )
    return config_scheme.check(raw_config)


def build_configuration(raw_config, selected_sdk):
    # type: (dict, str) -> Configuration
    sanitized_raw_config = sanitize_raw_config(raw_config)
    selected_sdk_conf = sanitized_raw_config.pop(selected_sdk, {})
    combined_raw_config = sanitized_raw_config.copy()
    combined_raw_config.update(selected_sdk_conf)
    conf = Configuration()
    for key, val in combined_raw_config.items():
        setattr(conf, key, val)
    return conf
