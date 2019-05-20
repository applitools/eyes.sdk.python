from __future__ import absolute_import

import time
import typing
from datetime import datetime

from applitools.common import MatchResult, RunningSession, logger
from applitools.common.errors import OutOfBoundsError
from applitools.common.geometry import Region
from applitools.common.match import ImageMatchSettings
from applitools.common.match_window_data import MatchWindowData, Options
from applitools.common.utils import image_utils
from applitools.common.visual_grid import VisualGridSelector
from applitools.core.capture import AppOutputProvider, AppOutputWithScreenshot

from .fluent import CheckSettings, GetFloatingRegion, GetRegion

if typing.TYPE_CHECKING:
    from typing import List, Text, Optional, Union
    from applitools.common import FloatingMatchSettings, EyesScreenshot
    from applitools.common.utils.custom_types import Num, UserInputs
    from applitools.core.server_connector import ServerConnector
    from .eyes_base import EyesBase

    GET_REGION = Union[GetRegion, GetFloatingRegion]
    REGION = Union[Region, FloatingMatchSettings]

__all__ = ("MatchWindowTask",)


def _collect_regions(region_providers, screenshot, eyes):
    # type: (List[GET_REGION], EyesScreenshot, EyesBase) -> List[REGION]
    collected = []  # type: List[REGION]
    for provider in region_providers:
        try:
            regions = provider.get_regions(eyes, screenshot)
            collected.extend(regions)
        except OutOfBoundsError:
            logger.warning("Region was out of bounds")
    return collected


def collect_regions_from_selectors(image_match_settings, regions, region_selectors):
    # type: (ImageMatchSettings, List[Region],List[VisualGridSelector]) -> ImageMatchSettings
    if not regions:
        return image_match_settings
    # TODO: implement function
    return image_match_settings


def collect_regions_from_screenshot(
    check_settings, image_match_settings, screenshot, eyes
):
    # type: (CheckSettings, ImageMatchSettings, EyesScreenshot, EyesBase) -> ImageMatchSettings

    image_match_settings.ignore = _collect_regions(  # type: ignore
        check_settings.values.ignore_regions, screenshot, eyes
    )
    image_match_settings.layout = _collect_regions(  # type: ignore
        check_settings.values.layout_regions, screenshot, eyes
    )
    image_match_settings.strict = _collect_regions(  # type: ignore
        check_settings.values.strict_regions, screenshot, eyes
    )
    image_match_settings.content = _collect_regions(  # type: ignore
        check_settings.values.content_regions, screenshot, eyes
    )
    image_match_settings.floating = _collect_regions(  # type: ignore
        check_settings.values.floating_regions, screenshot, eyes
    )
    return image_match_settings


class MatchWindowTask(object):
    """
    Handles matching of output with the expected output
    (including retry and 'ignore mismatch' when needed).
    """

    MATCH_INTERVAL_SEC = 0.5

    def __init__(
        self,
        server_connector,  # type: ServerConnector
        running_session,  # type: RunningSession
        retry_timeout_ms,  # type: Num
        eyes,  # type: EyesBase
        app_output_provider=None,  # type: Optional[AppOutputProvider]
    ):
        # type: (...) -> None
        """
        Ctor.

        :param server_connector: The agent connector to use for communication.
        :param running_session:  The current eyes session.
        :param retry_timeout_ms: The default match timeout. (milliseconds)
        :param eyes: The Eyes instance which created this task.
        :param app_output_provider: A callback for getting the application output
                                    when performing match.
       """
        self._server_connector = server_connector
        self._running_session = running_session
        self._eyes = eyes
        self._app_output_provider = app_output_provider
        self._default_retry_timeout_ms = retry_timeout_ms  # type: Num

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
        retry_timeout_ms,  # type: Num
    ):
        if retry_timeout_ms is None or retry_timeout_ms < 0:
            retry_timeout_ms = self._default_retry_timeout_ms
        logger.debug("retry_timeout = {} ms".format(retry_timeout_ms))

        retry_timeout_sec = retry_timeout_ms / 1000.0
        screenshot = self._take_screenshot(
            user_inputs,
            region,
            tag,
            should_run_once_on_timeout,
            ignore_mismatch,
            check_settings,
            retry_timeout_sec,
        )
        if ignore_mismatch:
            return self._match_result
        self._update_last_screenshot(screenshot)
        self._update_bounds(region)
        return self._match_result

    def perform_match(
        self,
        app_output,  # type: AppOutputWithScreenshot
        name,  # type: Text
        ignore_mismatch,  # type: bool
        image_match_settings,  # type: ImageMatchSettings
        eyes,  # type: EyesBase
        user_inputs=None,  # type: Optional[UserInputs]
        regions=None,  # type: Optional[List[Region]]
        region_selectors=None,  # type: Optional[List[VisualGridSelector]]
        check_settings=None,  # type: Optional[CheckSettings]
    ):
        screenshot = app_output.screenshot
        if check_settings and screenshot:
            image_match_settings = collect_regions_from_screenshot(
                check_settings, image_match_settings, screenshot, eyes
            )
        elif regions and region_selectors:
            image_match_settings = collect_regions_from_selectors(
                image_match_settings, regions, region_selectors
            )

        user_inputs = user_inputs or []
        agent_setup = self._eyes.agent_setup
        return self._perform_match(
            user_inputs,
            app_output,
            name,
            ignore_mismatch,
            image_match_settings,
            agent_setup,
        )

    def _perform_match(
        self,
        user_inputs,  # type: UserInputs
        app_output_width_screenshot,  # type: AppOutputWithScreenshot
        name,  # type: Text
        ignore_mismatch,  # type: bool
        image_match_settings,  # type: ImageMatchSettings
        agent_setup,  # type: Text
    ):
        screenshot = app_output_width_screenshot.screenshot
        app_output = app_output_width_screenshot.app_output
        if screenshot:
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
            agent_setup=agent_setup,
        )
        return self._server_connector.match_window(
            self._running_session, match_window_data
        )

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
                self._last_screenshot_bounds = Region(0, 0, 999999999999, 999999999999)
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
        retry_timeout_sec,
    ):
        time_start = datetime.now()
        if retry_timeout_sec == 0 or should_run_once_on_timeout:
            if should_run_once_on_timeout:
                time.sleep(retry_timeout_sec)

            screenshot = self._try_take_screenshot(
                user_inputs, region, tag, ignore_mismatch, check_settings
            )
        else:
            screenshot = self._retry_taking_screenshot(
                user_inputs,
                region,
                tag,
                ignore_mismatch,
                check_settings,
                retry_timeout_sec,
            )
        time_end = datetime.now()
        summary_ms = (time_end - time_start).seconds * 1000
        logger.debug(
            "MatchWindowTask._take_screenshot completed in {} ms".format(summary_ms)
        )
        return screenshot

    def _try_take_screenshot(
        self, user_inputs, region, tag, ignore_mismatch, check_settings
    ):
        app_output = self._app_output_provider.get_app_output(
            region, self._last_screenshot, check_settings
        )
        image_match_settings = ImageMatchSettings(
            match_level=check_settings.values.match_level,
            exact=None,
            ignore_caret=check_settings.values.ignore_caret,
            send_dom=check_settings.values.send_dom,
            use_dom=check_settings.values.use_dom,
            enable_patterns=check_settings.values.enable_patterns,
        )
        self._match_result = self.perform_match(
            app_output,
            tag,
            ignore_mismatch,
            image_match_settings,
            self._eyes,
            user_inputs,
            check_settings=check_settings,
        )
        return app_output.screenshot

    def _retry_taking_screenshot(
        self,
        user_inputs,
        region,
        tag,
        ignore_mismatch,
        check_settings,
        retry_timeout_sec,
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
            retry_timeout_sec,
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
        retry_timeout_sec,
        retry_sec,
        start,
        screenshot=None,
    ):
        if retry_sec >= retry_timeout_sec:
            return screenshot

        time.sleep(self.MATCH_INTERVAL_SEC)

        new_screenshot = self._try_take_screenshot(
            user_inputs,
            region,
            tag,
            ignore_mismatch=True,
            check_settings=check_settings,
        )
        if self._match_result.as_expected:
            return new_screenshot

        retry_sec = (start - datetime.now()).seconds
        return self._taking_screenshot_loop(
            user_inputs,
            region,
            tag,
            ignore_mismatch,
            check_settings,
            retry_timeout_sec,
            retry_sec,
            start,
            new_screenshot,
        )
