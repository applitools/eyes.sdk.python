import os
from enum import Enum
from typing import Text

import trafaret as trf
import yaml
from EyesLibrary.errors import EyesLibConfigParsingError, EyesLibValueError

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
from applitools.common.utils.compat import raise_from
from applitools.selenium import BatchInfo, Configuration


class SelectedRunner(Enum):
    selenium = "selenium"
    selenium_ufg = "selenium_ufg"
    appium = "appium"


class KeyNameMixin(object):
    def __init__(self, key_name):
        self.key_name = key_name


class ToEnumTrafaret(trf.Trafaret):
    def __init__(self, convert_to_enum):
        self.converter = convert_to_enum

    def check_and_return(self, value, context=None):
        try:
            return getattr(self.converter, value)
        except AttributeError:
            raise trf.DataError(
                "Incorrect value `{val}`. Possible variants: {possible_vals}".format(
                    val=value,
                    possible_vals=", ".join(e.name for e in self.converter),
                ),
                value=value,
                trafaret=self,
            )


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
        sanitized = self.scheme.check(value, context=context)
        batch = BatchInfo()
        for key, val in sanitized.items():
            setattr(batch, key, val)
        return batch


class ViewPortTrafaret(trf.Trafaret, KeyNameMixin):
    scheme = trf.Dict(width=trf.Int, height=trf.Int)

    def check_and_return(self, value, context=None):
        try:
            sanitized = self.scheme.check(value, context)
        except trf.DataError:
            raise trf.DataError("Incorrect value in")
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
            trf.Key("baseline_env_name", optional=True): trf.String,
            trf.Key("save_diffs", optional=True): trf.Bool,
            trf.Key("app_name", optional=True): trf.String,
            trf.Key("viewport_size", optional=True): ViewPortTrafaret("viewport_size"),
            trf.Key("match_timeout", optional=True): trf.Int,
            trf.Key("save_new_tests", optional=True): trf.Bool,
            trf.Key("save_failed_tests", optional=True): trf.Bool,
            trf.Key("properties", optional=True): trf.List(
                trf.Dict(name=trf.String, value=trf.String)
            ),
        },
    )
    selenium_scheme = shared_scheme + trf.Dict(
        {
            trf.Key("force_full_page_screenshot", optional=True): trf.Bool,
            trf.Key("wait_before_screenshots", optional=True): trf.Int,
            trf.Key("stitch_mode", optional=True): ToEnumTrafaret(StitchMode),
            trf.Key("hide_scrollbars", optional=True): trf.Bool,
            trf.Key("hide_caret", optional=True): trf.Bool,
        },
    )
    selenium_ufg_scheme = shared_scheme + trf.Dict(
        {
            trf.Key("runner_options", optional=True): trf.Dict(concurrency=trf.Int),
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
    )
    appium_scheme = shared_scheme + trf.Dict(
        {
            trf.Key("is_simulator", optional=True): trf.Bool,
        },
    )
    scheme = shared_scheme + trf.Dict(
        {
            trf.Key("selenium", optional=True): shared_scheme + selenium_scheme,
            trf.Key("appium", optional=True): shared_scheme + appium_scheme,
            trf.Key("selenium_ufg", optional=True): shared_scheme + selenium_ufg_scheme,
        },
    )

    def __init__(self, selected_sdk, add_to_config):
        # type: (SelectedRunner, Configuration) -> None
        self._selected_runner = selected_sdk
        self._exists_configuration = add_to_config

    def check_and_return(self, value, context=None):
        sanitized = self.scheme.check(value, context)
        if self._selected_runner:
            selected_sdk_conf = sanitized.pop(self._selected_runner, {})
        else:
            # Parse full config if no runner specified
            selected_sdk_conf = sanitized.pop(SelectedRunner.selenium, {})
            selected_sdk_conf.update(sanitized.pop(SelectedRunner.selenium_ufg, {}))
            selected_sdk_conf.update(sanitized.pop(SelectedRunner.appium, {}))

        combined_raw_config = sanitized.copy()
        combined_raw_config.update(selected_sdk_conf)
        conf = self._exists_configuration or Configuration()
        for key, val in combined_raw_config.items():
            setattr(conf, key, val)
        return conf


def try_parse_runner(runner):
    # type: (Text) -> SelectedRunner
    try:
        return SelectedRunner(runner)
    except ValueError as e:
        raise_from(
            EyesLibValueError(
                "Incorrect value for `runner`: `{val}`. "
                "\n\tPossible variants:"
                "\n\t\t{possible_vals}".format(
                    val=runner,
                    possible_vals=", ".join(e.name for e in SelectedRunner),
                )
            ),
            e,
        )


def try_parse_configuration(
    config_path, selected_runner, origin_configuration, suite_source
):
    # type: (Text, SelectedRunner, Configuration, Text) -> Configuration
    if not os.path.isabs(config_path):
        # if config path is not absolute that count test suite directory as root
        suite_path = os.path.dirname(suite_source)
        config_path = os.path.join(suite_path, config_path)

    if not os.path.exists(config_path):
        raise EyesLibValueError(
            "Not found configuration file within path: {}".format(config_path)
        )

    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f.read())

    # It's better to raise here library error but for some reason raise_from
    # suppress original error message
    return ConfigurationTrafaret(selected_runner, origin_configuration).check(
        raw_config
    )
