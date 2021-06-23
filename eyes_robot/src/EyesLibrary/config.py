import trafaret as t
from trafaret.keys import subdict

from applitools.common import (
    DeviceName,
    IosDeviceName,
    IosVersion,
    ProxySettings,
    ScreenOrientation,
    StitchMode,
    VisualGridOption,
)
from applitools.common.selenium import BrowserType
from applitools.core import Feature
from applitools.selenium import BatchInfo, Configuration


def _enum_to_list_of_values(enum):
    return [e.value for e in enum]


def sanitize_raw_config(raw_config):
    # type: (dict) -> dict

    viewport_scheme = t.Dict(width=t.Int, height=t.Int)
    batch_scheme = t.Dict(
        {
            t.Key("id", optional=True): t.String,
            t.Key("name", optional=True): t.String,
            t.Key("batch_sequence_name", optional=True): t.String,
            t.Key("started_at", optional=True): t.DateTime,
        },
    )
    config_scheme = t.Dict(
        {
            t.Key("server_url", optional=True): t.URL,
            t.Key("batch", optional=True): batch_scheme,
            t.Key("proxy", optional=True): t.Dict(
                {t.Key("url") >> "host_or_url": t.URL}
            )
            | t.Dict(
                {
                    t.Key("host") >> "host_or_url": t.String,
                    "port": t.Int,
                    "username": t.String,
                    "password": t.String,
                    "shceme": t.String,
                },
            ),
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
            t.Key("viewport_size", optional=True): viewport_scheme,
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
                    t.Key("visual_grid_options", optional=True): t.List(
                        t.Dict({"key": t.String, "value": t.String})
                    ),
                    t.Key("disable_browser_fetching", optional=True): t.Bool,
                    t.Key("enable_cross_origin_rendering", optional=True): t.Bool,
                    t.Key("dont_use_cookies", optional=True): t.Bool,
                    t.Key("layout_breakpoints", optional=True): t.Bool | t.List(t.Int),
                    t.Key("devices", optional=True): t.List(
                        t.Dict(
                            {
                                "device_name": t.Enum(
                                    *_enum_to_list_of_values(DeviceName)
                                ),
                                t.Key("screen_orientation", optional=True): t.Enum(
                                    *_enum_to_list_of_values(ScreenOrientation)
                                ),
                            }
                        )
                    ),
                    t.Key("ios_devices", optional=True): t.List(
                        t.Dict(
                            {
                                "device_name": t.Enum(
                                    *_enum_to_list_of_values(IosDeviceName)
                                ),
                                t.Key("screen_orientation", optional=True): t.Enum(
                                    *_enum_to_list_of_values(ScreenOrientation)
                                ),
                                t.Key("ios_version", optional=True): t.Enum(
                                    *_enum_to_list_of_values(IosVersion)
                                ),
                            }
                        )
                    ),
                    t.Key("browsers", optional=True): t.List(
                        t.Dict(
                            {
                                "browser_type": t.Enum(
                                    *_enum_to_list_of_values(BrowserType)
                                ),
                                "width": t.Int,
                                "height": t.Int,
                            }
                        )
                    ),
                },
                allow_extra="*",
            ),
        },
        allow_extra="*",
    )
    return config_scheme.check(raw_config)


def build_configuration(sanitized_raw_config, selected_sdk):
    # type: (dict, str) -> Configuration
    selected_sdk_conf = sanitized_raw_config.pop(selected_sdk, {})
    raw_batch = sanitized_raw_config.pop("batch", None)
    raw_proxy = sanitized_raw_config.pop("proxy", None)
    raw_visual_grid_options = selected_sdk_conf.pop("visual_grid_options", None)
    combined_raw_config = {**sanitized_raw_config, **selected_sdk_conf}
    conf = Configuration()
    for key, val in combined_raw_config.items():
        setattr(conf, key, val)

    if raw_batch:
        batch = BatchInfo()
        for key, val in raw_batch.items():
            setattr(batch, key, val)
        conf.batch = batch

    if raw_proxy:
        proxy = ProxySettings(host_or_url=raw_proxy.pop("host_or_url"), **raw_proxy)
        conf.proxy = proxy
    if raw_visual_grid_options:
        options = [VisualGridOption(**dct) for dct in raw_visual_grid_options]
        conf.visual_grid_options = options
    return conf
