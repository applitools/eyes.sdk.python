from __future__ import absolute_import

import time
import typing
from datetime import datetime

from applitools.common import (
    AppOutputProvider,
    AppOutputWithScreenshot,
    MatchResult,
    RunningSession,
    logger,
)
from applitools.common.errors import OutOfBoundsError
from applitools.common.geometry import Region
from applitools.common.match import ImageMatchSettings
from applitools.common.match_window_data import MatchWindowData, Options
from applitools.common.utils import general_utils, image_utils

from .fluent import CheckSettings, GetRegion

if typing.TYPE_CHECKING:
    from typing import List, Text, Optional
    from applitools.common.capture import EyesScreenshot
    from applitools.common.utils.custom_types import Num, UserInputs
    from applitools.core.server_connector import ServerConnector
    from .eyes_base import EyesBase

__all__ = ("MatchWindowTask",)


class MatchWindowTask(object):
    """
    Handles matching of output with the expected output
    (including retry and 'ignore mismatch' when needed).
    """

    MATCH_INTERVAL = 0.5  # sec
    MINIMUM_MATCH_TIMEOUT = 60  # Milliseconds

    def __init__(
        self,
        server_connector,  # type: ServerConnector
        running_session,  # type: RunningSession
        retry_timeout,  # type: Num
        eyes,  # type: EyesBase
        app_output_provider,  # type: AppOutputProvider
    ):
        # type: (...) -> None
        """
        Ctor.

        :param server_connector: The agent connector to use for communication.
        :param running_session:  The current eyes session.
        :param retry_timeout: The default match timeout. (milliseconds)
        :param eyes: The Eyes instance which created this task.
        :param app_output_provider: A callback for getting the application output
                                    when performing match.
       """
        self._server_connector = server_connector
        self._running_session = running_session
        self._eyes = eyes
        self._app_output_provider = app_output_provider
        self._default_retry_timeout = (
            retry_timeout / 1000.0
        )  # type: Num # since we want the time in seconds.

        self._match_result = None  # type: MatchResult
        self._last_screenshot = None  # type: Optional[EyesScreenshot]

    @property
    def last_screenshot(self):
        return self._last_screenshot

    @property
    def last_screenshot_bounds(self):
        return self._last_screenshot_bounds

    def match_window(
        self,
        user_inputs,  # type: UserInputs
        region,  # type: Region
        tag,  # type: Text
        should_run_once_on_timeout,  # type: bool
        ignore_mismatch,  # type: bool
        check_settings,  # type: CheckSettings
        retry_timeout,  # type: int
    ):
        if retry_timeout is None or retry_timeout < 0:
            retry_timeout = self._default_retry_timeout
        logger.info("retry_timeout = {}".format(retry_timeout))

        screenshot = self._take_screenshot(
            user_inputs,
            region,
            tag,
            should_run_once_on_timeout,
            ignore_mismatch,
            check_settings,
            retry_timeout,
        )
        if ignore_mismatch:
            return self._match_result
        self._update_last_screenshot(screenshot)
        self._update_bounds(region)
        return self._match_result

    def perform_match(
        self,
        user_inputs,  # type: UserInputs
        app_output_width_screenshot,  # type: AppOutputWithScreenshot
        name,  # type: Text
        ignore_mismatch,  # type: bool
        image_match_settings,  # type: ImageMatchSettings
    ):
        screenshot = app_output_width_screenshot.screenshot
        app_output = app_output_width_screenshot.app_output
        app_output.screenshot64 = image_utils.get_base64(screenshot.image)

        match_window_data = MatchWindowData(
            ignore_mismatch=ignore_mismatch,
            user_inputs=user_inputs,
            options=Options(
                name=name,
                user_inputs=user_inputs,
                ignore_mismatch=ignore_mismatch,
                ignore_match=False,
                force_mismatch=False,
                force_match=False,
                image_match_settings=image_match_settings,
            ),
            app_output=app_output,
            tag=name,
        )
        return self._server_connector.match_window(
            self._running_session, match_window_data
        )

    def _create_image_match_settings(self, check_settings, screenshot):
        # type: (CheckSettings, EyesScreenshot) -> ImageMatchSettings
        default = general_utils.use_default_if_none_factory(
            self._eyes.default_match_settings, check_settings.values
        )
        match_level = default("match_level")
        ignore_caret = default("ignore_caret")
        send_dom = default("send_dom")
        use_dom = default("use_dom")
        enable_patterns = default("enable_patterns")

        image_match_settings = ImageMatchSettings(
            match_level=match_level,
            exact=None,
            ignore_caret=ignore_caret,
            send_dom=send_dom,
            use_dom=use_dom,
            enable_patterns=enable_patterns,
        )
        self._collect_simple_regions(check_settings, image_match_settings, screenshot)
        self._collect_float_regions(check_settings, image_match_settings, screenshot)
        return image_match_settings

    def _collect_simple_regions(self, check_settings, image_match_settings, screenshot):
        # type: (CheckSettings, ImageMatchSettings, EyesScreenshot) -> None

        image_match_settings.ignore = self._collect_regions(
            check_settings.values.ignore_regions, screenshot
        )
        image_match_settings.layout = self._collect_regions(
            check_settings.values.layout_regions, screenshot
        )
        image_match_settings.strict = self._collect_regions(
            check_settings.values.strict_regions, screenshot
        )
        image_match_settings.content = self._collect_regions(
            check_settings.values.content_regions, screenshot
        )

    def _collect_float_regions(self, check_settings, image_match_settings, screenshot):
        # type: (CheckSettings, ImageMatchSettings, EyesScreenshot) -> None
        image_match_settings.floating = self._collect_regions(
            check_settings.values.floating_regions, screenshot
        )

    def _collect_regions(self, region_providers, screenshot):
        # type: (List[GetRegion], EyesScreenshot) -> List[Region]
        eyes = self._eyes
        regions = []
        for provider in region_providers:
            try:
                region = provider.get_region(eyes, screenshot)
                regions.append(region)
            except OutOfBoundsError:
                logger.warning("Region was out of bounds")
        return regions

    def _update_last_screenshot(self, screenshot):
        if screenshot:
            self._last_screenshot = screenshot

    def _update_bounds(self, region):
        if region.is_size_empty:
            if self._last_screenshot:
                self._last_screenshot_bounds = Region(
                    0,
                    0,
                    self._last_screenshot.image.width,
                    self._last_screenshot.image.height,
                )
            else:
                # We set an "infinite" image size since we don't know what the
                # screenshot size is...
                self._last_screenshot_bounds = Region(0, 0, float("inf"), float("inf"))
        else:
            self._last_screenshot_bounds = region

    def _take_screenshot(
        self,
        user_inputs,
        region,
        tag,
        should_run_once_on_timeout,
        ignore_mismatch,
        check_settings,
        retry_timeout,
    ):
        time_start = datetime.now()
        if retry_timeout == 0 or should_run_once_on_timeout:
            if should_run_once_on_timeout:
                time.sleep(retry_timeout)

            screenshot = self._try_take_screenshot(
                user_inputs, region, tag, ignore_mismatch, check_settings
            )
        else:
            screenshot = self._retry_taking_screenshot(
                user_inputs, region, tag, ignore_mismatch, check_settings, retry_timeout
            )
        time_end = datetime.now()
        summary = time_end - time_start
        logger.info("Completed in {} ms".format(summary.microseconds))
        return screenshot

    def _try_take_screenshot(
        self, user_inputs, region, tag, ignore_mismatch, check_settings
    ):
        app_output = self._app_output_provider.get_app_output(
            region, self._last_screenshot, check_settings
        )
        screenshot = app_output.screenshot
        match_settings = self._create_image_match_settings(check_settings, screenshot)
        self._match_result = self.perform_match(
            user_inputs, app_output, tag, ignore_mismatch, match_settings
        )
        return screenshot

    def _retry_taking_screenshot(
        self, user_inputs, region, tag, ignore_mismatch, check_settings, retry_timeout
    ):
        start = datetime.now()  # Start the retry timer.
        retry = (datetime.now() - start).seconds

        # The match retry loop.
        screenshot = self._taking_screenshot_loop(
            user_inputs,
            region,
            tag,
            ignore_mismatch,
            check_settings,
            retry_timeout,
            retry,
            start,
        )
        # If we're here because we haven't found a match yet, try once more
        if not self._match_result.as_expected:
            return self._try_take_screenshot(
                user_inputs, region, tag, ignore_mismatch, check_settings
            )
        return screenshot

    def _taking_screenshot_loop(
        self,
        user_inputs,
        region,
        tag,
        ignore_mismatch,
        check_settings,
        retry_timeout,
        retry,
        start,
        screenshot=None,
    ):
        if retry >= retry_timeout:
            return screenshot

        time.sleep(self.MATCH_INTERVAL)

        new_screenshot = self._try_take_screenshot(
            user_inputs,
            region,
            tag,
            ignore_mismatch=True,
            check_settings=check_settings,
        )
        if self._match_result.as_expected:
            return new_screenshot

        retry = (start - datetime.now()).seconds
        return self._taking_screenshot_loop(
            user_inputs,
            region,
            tag,
            ignore_mismatch,
            check_settings,
            retry_timeout,
            retry,
            start,
            new_screenshot,
        )
