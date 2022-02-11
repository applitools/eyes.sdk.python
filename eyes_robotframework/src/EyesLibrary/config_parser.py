from __future__ import absolute_import, unicode_literals

import itertools
import os
from enum import Enum
from typing import Callable, Text, Type

import trafaret as trf
import yaml
from six import raise_from

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
from applitools.selenium import BatchInfo, RunnerOptions

from .config import RobotConfiguration
from .errors import EyesLibraryConfigError, EyesLibraryValueError
from .utils import get_enum_by_name, get_enum_by_upper_name, parse_viewport_size


class SelectedRunner(Enum):
    web = "web"
    web_ufg = "web_ufg"
    mobile_native = "mobile_native"


class RobotStitchMode(Enum):
    CSS = StitchMode.CSS.value
    SCROLL = StitchMode.Scroll.value


class _ToEnumTrafaret(trf.Trafaret):
    def __init__(self, convert_to_enum):
        # type: (Type[Enum])->None
        self.converter = convert_to_enum

    @property
    def to_enum_func(self):
        # type: () -> Callable[[Text, Type[Enum]], Enum]
        return NotImplemented

    def check_and_return(self, value, context=None):
        try:
            return self.to_enum_func(value, self.converter)
        except ValueError:
            raise trf.DataError(
                "Incorrect value `{val}`. Possible variants: {possible_vals}".format(
                    val=value,
                    possible_vals=", ".join(e.name for e in self.converter),
                ),
                value=value,
                trafaret=self,
            )


class TextToEnumTrafaret(_ToEnumTrafaret):
    @property
    def to_enum_func(self):
        # type: () -> Callable[[Text, Type[Enum]], Enum]
        return get_enum_by_name


class UpperTextToEnumTrafaret(_ToEnumTrafaret):
    @property
    def to_enum_func(self):
        # type: () -> Callable[[Text, Type[Enum]], Enum]
        return get_enum_by_upper_name


class BatchInfoTrafaret(trf.Trafaret):
    scheme = trf.Dict(
        {
            trf.Key("id", optional=True): trf.String,
            trf.Key("name", optional=True): trf.String,
            trf.Key("batch_sequence_name", optional=True)
            >> "sequence_name": trf.String,
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


class ViewPortTrafaret(trf.Trafaret):
    scheme = trf.Dict(width=trf.Int, height=trf.Int) | parse_viewport_size

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
                "browser_type": UpperTextToEnumTrafaret(BrowserType),
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
                "device_name": TextToEnumTrafaret(IosDeviceName),
                trf.Key("screen_orientation", optional=True): UpperTextToEnumTrafaret(
                    ScreenOrientation
                ),
                trf.Key("ios_version", optional=True): UpperTextToEnumTrafaret(
                    IosVersion
                ),
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
                "device_name": TextToEnumTrafaret(DeviceName),
                trf.Key("screen_orientation", optional=True): UpperTextToEnumTrafaret(
                    ScreenOrientation
                ),
            }
        )
    )

    def check_and_return(self, value, context=None):
        sanitized = self.scheme.check(value, context)
        return [ChromeEmulationInfo(**dct) for dct in sanitized]


class RunnerOptionsTrafaret(trf.Trafaret):
    scheme = trf.Dict({trf.Key("test_concurrency"): trf.Int})

    def check_and_return(self, value, context=None):
        sanitized = self.scheme.check(value, context)
        return RunnerOptions().test_concurrency(sanitized["test_concurrency"])


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


class BrowsersTrafaret(trf.Trafaret):
    scheme = trf.Dict(
        {
            trf.Key("desktop", optional=True): DesktopBrowserInfoTrafaret,
            trf.Key("ios", optional=True): IosDeviceInfoTrafaret,
            trf.Key("chrome_emulation", optional=True): ChromeEmulationInfoTrafaret,
        }
    )

    def check_and_return(self, value, context=None):
        sanitized = self.scheme.check(value, context)
        desktop = sanitized.pop("desktop", [])
        ios = sanitized.pop("ios", [])
        chrome_emulation = sanitized.pop("chrome_emulation", [])
        return list(itertools.chain(desktop, ios, chrome_emulation))


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
            trf.Key("viewport_size", optional=True): ViewPortTrafaret,
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
            trf.Key("stitch_mode", optional=True): UpperTextToEnumTrafaret(
                RobotStitchMode
            ),
            trf.Key("hide_scrollbars", optional=True): trf.Bool,
            trf.Key("hide_caret", optional=True): trf.Bool,
        },
    )
    selenium_ufg_scheme = shared_scheme + trf.Dict(
        {
            trf.Key("runner_options", optional=True): RunnerOptionsTrafaret,
            trf.Key("visual_grid_options", optional=True): VisualGridOptionsTrafaret,
            trf.Key("disable_browser_fetching", optional=True): trf.Bool,
            trf.Key("enable_cross_origin_rendering", optional=True): trf.Bool,
            trf.Key("dont_use_cookies", optional=True): trf.Bool,
            trf.Key("layout_breakpoints", optional=True): trf.Bool | trf.List(trf.Int),
            trf.Key("browsers", optional=True) >> "_browsers_info": BrowsersTrafaret,
        },
    )
    appium_scheme = shared_scheme + trf.Dict(
        {
            trf.Key("is_simulator", optional=True): trf.Bool,
        },
    )
    scheme = shared_scheme + trf.Dict(
        {
            trf.Key("web", optional=True): shared_scheme + selenium_scheme,
            trf.Key("web_ufg", optional=True): shared_scheme + selenium_ufg_scheme,
            trf.Key("mobile_native", optional=True): shared_scheme + appium_scheme,
        },
    )

    def __init__(self, selected_sdk, add_to_config):
        # type: (SelectedRunner, RobotConfiguration) -> None
        self._selected_runner = selected_sdk
        self._exists_configuration = add_to_config

    def check_and_return(self, value, context=None):
        sanitized = self.scheme.check(value, context)
        selected_sdk_conf = sanitized[self._selected_runner.value]

        combined_raw_config = sanitized.copy()
        # we need only shared data here  TODO: make it nicer
        combined_raw_config.pop(SelectedRunner.web.value)
        combined_raw_config.pop(SelectedRunner.web_ufg.value)
        combined_raw_config.pop(SelectedRunner.mobile_native.value)

        # add config for selected runner
        combined_raw_config.update(selected_sdk_conf)
        for key, val in combined_raw_config.items():
            setattr(self._exists_configuration, key, val)
        return self._exists_configuration


def try_parse_runner(runner):
    # type: (Text) -> SelectedRunner
    try:
        return SelectedRunner(runner)
    except ValueError as e:
        raise_from(
            EyesLibraryValueError(
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
    config_path, selected_runner, origin_configuration, suite_path
):
    # type: (Text, SelectedRunner, RobotConfiguration, Text) -> RobotConfiguration
    if not os.path.isabs(config_path):
        # if config path is not absolute that count test suite directory as root
        config_path = os.path.join(suite_path, config_path)

    if not os.path.exists(config_path):
        raise EyesLibraryConfigError(
            "The configuration file was not found in the following directory: {}\n"
            "You could initialize config file with command: \n\t"
            "`python -m EyesLibrary init-config`".format(config_path)
        )

    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f.read())

    # It's better to raise here library error but for some reason raise_from
    # suppress original error message
    return ConfigurationTrafaret(selected_runner, origin_configuration).check(
        raw_config
    )
