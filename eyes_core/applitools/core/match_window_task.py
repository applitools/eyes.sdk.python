from __future__ import absolute_import

import typing
from datetime import datetime

from applitools.common import FloatingMatchSettings, MatchResult, RunningSession, logger
from applitools.common.errors import OutOfBoundsError
from applitools.common.geometry import AccessibilityRegion, Point, Region
from applitools.common.match import ImageMatchSettings
from applitools.common.match_window_data import MatchWindowData, Options
from applitools.common.ultrafastgrid import VisualGridSelector
from applitools.common.utils import datetime_utils, image_utils
from applitools.core.capture import AppOutputProvider, AppOutputWithScreenshot
from applitools.core.fluent.region import (
    AccessibilityRegionByRectangle,
    FloatingRegionByRectangle,
    RegionByRectangle,
)

from .fluent import CheckSettings, GetAccessibilityRegion, GetFloatingRegion, GetRegion

if typing.TYPE_CHECKING:
    from typing import List, Optional, Text, Union

    from applitools.common import EyesScreenshot
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


def filter_empty_entries(regions, location):
    return [region.offset(-location) for region in regions if region.area != 0]


def filter_empty_entries_and_combine(regions, location, region_selectors):
    for i, reg in enumerate(regions):
        if reg.area == 0:
            continue
        reg = reg.offset(-location)
        vgs = region_selectors[i]
        yield reg, vgs.category


def collect_regions_from_selectors(image_match_settings, regions, region_selectors):
    # type:(ImageMatchSettings,List[Region],List[List[VisualGridSelector]])->ImageMatchSettings
    if not regions:
        return image_match_settings
    logger.debug(
        """
    start collect_regions_from_selectors()

        regions: {}
        region_selectors: {}
    """.format(
            regions, region_selectors
        )
    )
    mutable_regions = [
        [],  # Ignore Regions
        [],  # Layout Regions
        [],  # Strict Regions
        [],  # Content Regions
        [],  # Floating Regions
        [],  # Accessibility Regions
        [],  # Target Element Location
    ]
    r_selector_counts = [len(r) for r in region_selectors]  # mapping of
    prev_count = 0
    for i, (selectors_count, m_specific_regions) in enumerate(
        zip(r_selector_counts, mutable_regions)
    ):
        if selectors_count == 0:
            continue
        next_count = prev_count + selectors_count
        for region_selector, region in zip(
            region_selectors[i], regions[prev_count:next_count]
        ):
            padding = getattr(region_selector.category, "padding", None)
            if padding:
                region = region.padding(padding)
            m_specific_regions.append(region)
        prev_count = next_count

    location = Point.ZERO()

    # If target element location available
    selector_regions_index = len(mutable_regions) - 1
    if mutable_regions[selector_regions_index]:
        location = mutable_regions[selector_regions_index][0].location

    image_match_settings.ignore_regions = filter_empty_entries(
        mutable_regions[0], location
    )
    image_match_settings.layout_regions = filter_empty_entries(
        mutable_regions[1], location
    )
    image_match_settings.strict_regions = filter_empty_entries(
        mutable_regions[2], location
    )
    image_match_settings.content_regions = filter_empty_entries(
        mutable_regions[3], location
    )
    image_match_settings.floating_match_settings = [
        FloatingMatchSettings(reg, gfr.floating_bounds)
        for (reg, gfr) in filter_empty_entries_and_combine(
            mutable_regions[4], location, region_selectors[4]
        )
        if isinstance(gfr, GetFloatingRegion)
    ]
    image_match_settings.accessibility = [
        AccessibilityRegion.from_(reg, gfr.accessibility_type)
        for (reg, gfr) in filter_empty_entries_and_combine(
            mutable_regions[5], location, region_selectors[5]
        )
        if isinstance(gfr, GetAccessibilityRegion)
    ]
    logger.debug(
        """
    finish collect_regions_from_selectors()

        image_match_settings: {}
    """.format(
            image_match_settings
        )
    )
    return image_match_settings


def _coded_regions(region_providers):
    regions = []
    coded_region_types = (
        RegionByRectangle,
        AccessibilityRegionByRectangle,
        FloatingRegionByRectangle,
    )
    for rp in region_providers:
        if isinstance(rp, coded_region_types):
            regions.extend(rp.get_regions(None, None))
    return regions


def collect_append_coded_regions(check_settings, image_match_settings):
    # type:(CheckSettings,ImageMatchSettings,EyesScreenshot,EyesBase)->ImageMatchSettings
    for ims_region, settings_region in (
        (image_match_settings.ignore_regions, check_settings.values.ignore_regions),
        (image_match_settings.layout_regions, check_settings.values.layout_regions),
        (image_match_settings.strict_regions, check_settings.values.strict_regions),
        (image_match_settings.content_regions, check_settings.values.content_regions),
        (
            image_match_settings.floating_match_settings,
            check_settings.values.floating_regions,
        ),
        (
            image_match_settings.accessibility,
            check_settings.values.accessibility_regions,
        ),
    ):
        ims_region.extend(_coded_regions(settings_region))

    logger.debug(
        """
    finish collect_append_coded_regions()

        image_match_settings: {}
    """.format(
            image_match_settings
        )
    )
    return image_match_settings


def collect_regions_from_screenshot(
    check_settings, image_match_settings, screenshot, eyes
):
    # type:(CheckSettings,ImageMatchSettings,EyesScreenshot,EyesBase)->ImageMatchSettings

    image_match_settings.ignore_regions = _collect_regions(  # type: ignore
        check_settings.values.ignore_regions, screenshot, eyes
    )
    image_match_settings.layout_regions = _collect_regions(  # type: ignore
        check_settings.values.layout_regions, screenshot, eyes
    )
    image_match_settings.strict_regions = _collect_regions(  # type: ignore
        check_settings.values.strict_regions, screenshot, eyes
    )
    image_match_settings.content_regions = _collect_regions(  # type: ignore
        check_settings.values.content_regions, screenshot, eyes
    )
    image_match_settings.floating_match_settings = _collect_regions(  # type: ignore
        check_settings.values.floating_regions, screenshot, eyes
    )
    image_match_settings.accessibility = _collect_regions(  # type: ignore
        check_settings.values.accessibility_regions, screenshot, eyes
    )
    logger.debug(
        """
    finish collect_regions_from_screenshot()

        image_match_settings: {}
    """.format(
            image_match_settings
        )
    )
    return image_match_settings


class MatchWindowTask(object):
    """
    Handles matching of output with the expected output
    (including retry and 'ignore mismatch' when needed).
    """

    _MATCH_INTERVAL_MS = 500  # ms

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

        self._match_result = None  # type: Optional[MatchResult]
        self._last_screenshot = None  # type: Optional[EyesScreenshot]
        self._last_screenshot_hash = None  # type: Optional[Text]

    @staticmethod
    def create_image_match_settings(check_settings, eyes, screenshot=None):
        # type: (CheckSettings, EyesBase, Options[EyesScreenshot])-> ImageMatchSettings
        img = ImageMatchSettings.create_from(eyes.configure.default_match_settings)
        img.accessibility_settings = eyes.configure.accessibility_validation

        # Set defaults if necessary
        if check_settings.values.match_level is not None:
            img.match_level = check_settings.values.match_level
        if check_settings.values.ignore_caret is not None:
            img.ignore_caret = check_settings.values.ignore_caret
        if check_settings.values.use_dom is not None:
            img.use_dom = check_settings.values.use_dom
        if check_settings.values.enable_patterns is not None:
            img.enable_patterns = check_settings.values.enable_patterns
        if check_settings.values.ignore_displacements is not None:
            img.ignore_displacements = check_settings.values.ignore_displacements
        if check_settings.values.match_level is not None:
            img.match_level = check_settings.values.match_level

        if screenshot:
            img = collect_regions_from_screenshot(check_settings, img, screenshot, eyes)
        return img

    @property
    def last_screenshot(self):
        # type: () -> EyesScreenshot
        return self._last_screenshot

    @property
    def last_screenshot_bounds(self):
        # type: () -> Region
        return self._last_screenshot_bounds

    def match_window(
        self,
        user_inputs,  # type: UserInputs
        region,  # type: Region
        should_run_once_on_timeout,  # type: bool
        check_settings,  # type: CheckSettings
        retry_timeout_ms,  # type: Num
        source,  # type: Optional[Text]
    ):
        # type: (...) -> MatchResult
        if retry_timeout_ms is None or retry_timeout_ms < 0:
            retry_timeout_ms = self._default_retry_timeout_ms
        logger.debug("retry_timeout = {} ms".format(retry_timeout_ms))

        # set hash to initial value
        self._last_screenshot_hash = None

        screenshot = self._take_screenshot(
            user_inputs,
            region,
            should_run_once_on_timeout,
            check_settings,
            retry_timeout_ms,
            source,
        )
        self._update_last_screenshot(screenshot)
        self._update_bounds(region)
        return self._match_result

    def perform_match(
        self,
        app_output,  # type: AppOutputWithScreenshot
        replace_last,  # type: bool
        image_match_settings,  # type: ImageMatchSettings
        eyes,  # type: EyesBase
        user_inputs=None,  # type: Optional[UserInputs]
        regions=None,  # type: Optional[List[Region]]
        region_selectors=None,  # type: Optional[List[List[VisualGridSelector]]]
        check_settings=None,  # type: Optional[CheckSettings]
        render_id=None,  # type: Optional[Text]
        source=None,  # type: Optional[Text]
    ):
        # type: (...) -> MatchResult

        screenshot = app_output.screenshot
        if check_settings and screenshot:
            image_match_settings = collect_regions_from_screenshot(
                check_settings, image_match_settings, screenshot, eyes
            )
        else:
            # visual grid
            if regions and region_selectors:
                image_match_settings = collect_regions_from_selectors(
                    image_match_settings, regions, region_selectors
                )
            if check_settings:
                image_match_settings = collect_append_coded_regions(
                    check_settings, image_match_settings
                )
        user_inputs = user_inputs or []
        agent_setup = logger.create_message_from_log(
            agent_id=self._eyes.base_agent_id,
            test_id="None",  # TODO: add value when test_id would be added
            stage=logger.Stage.CHECK,
            data={
                "configuration": self._eyes.configure,
                "checkSettings": check_settings.values,
            },
        )
        return self._perform_match(
            user_inputs,
            app_output,
            check_settings,
            replace_last,
            image_match_settings,
            agent_setup,
            render_id,
            source,
        )

    def _perform_match(
        self,
        user_inputs,  # type: UserInputs
        app_output_width_screenshot,  # type: AppOutputWithScreenshot
        check_settings,  # type: CheckSettings
        replace_last,  # type: bool
        image_match_settings,  # type: ImageMatchSettings
        agent_setup,  # type: Text
        render_id,  # type: Text
        source,  # type: Text
    ):
        # type: (...) -> MatchResult
        name = check_settings.values.name
        variant_id = check_settings.values.variation_group_id
        screenshot = app_output_width_screenshot.screenshot
        app_output = app_output_width_screenshot.app_output
        if screenshot:
            app_output.screenshot_bytes = image_utils.get_bytes(screenshot.image)

        match_window_data = MatchWindowData(
            ignore_mismatch=False,
            user_inputs=user_inputs,
            options=Options(
                name=name,
                user_inputs=user_inputs,
                replace_last=replace_last,
                ignore_mismatch=False,
                ignore_match=False,
                force_mismatch=False,
                force_match=False,
                image_match_settings=image_match_settings,
                source=source,
                render_id=render_id,
                variant_id=variant_id,
            ),
            app_output=app_output,
            tag=name,
            agent_setup=agent_setup,
            render_id=render_id,
        )
        return self._server_connector.match_window(
            self._running_session, match_window_data
        )

    def _update_last_screenshot(self, screenshot):
        # type: (EyesScreenshot) -> None
        if screenshot:
            self._last_screenshot = screenshot

    def _update_bounds(self, region):
        # type: (Region) -> None
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
        user_inputs,  # type: UserInputs
        region,  # type: Region
        should_run_once_on_timeout,  # type: bool
        check_settings,  # type: CheckSettings
        retry_timeout,  # type: int
        source,  # type: Optional[Text],
    ):
        # type: (...) -> EyesScreenshot

        time_start = datetime.now()
        if retry_timeout == 0 or should_run_once_on_timeout:
            if should_run_once_on_timeout:
                datetime_utils.sleep(retry_timeout)

            screenshot = self._try_take_screenshot(
                user_inputs, region, check_settings, source
            )
        else:
            screenshot = self._retry_taking_screenshot(
                user_inputs, region, check_settings, retry_timeout, source
            )
        time_end = datetime.now()
        summary_ms = datetime_utils.to_ms((time_end - time_start).seconds)
        logger.debug(
            "MatchWindowTask._take_screenshot completed in {} ms".format(summary_ms)
        )
        return screenshot

    def _try_take_screenshot(
        self,
        user_inputs,  # type: UserInputs
        region,  # type: Region
        check_settings,  # type: CheckSettings
        source,  # type: Optional[Text]
    ):
        # type: (...) -> EyesScreenshot
        app_output = self._app_output_provider.get_app_output(
            region, self._last_screenshot, check_settings
        )
        current_screenshot_hash = hash(app_output.screenshot)
        if current_screenshot_hash == self._last_screenshot_hash:
            logger.info("Got the same screenshot in retry. Not sending to the server")
            return app_output.screenshot

        image_match_settings = self.create_image_match_settings(
            check_settings, self._eyes
        )

        replace_last_if_not_first_run = self._last_screenshot_hash is not None
        self._match_result = self.perform_match(
            app_output,
            replace_last_if_not_first_run,
            image_match_settings,
            self._eyes,
            user_inputs,
            check_settings=check_settings,
            source=source,
        )
        self._last_screenshot_hash = current_screenshot_hash
        return app_output.screenshot

    def _retry_taking_screenshot(
        self,
        user_inputs,  # type: UserInputs
        region,  # type: Region
        check_settings,  # type: CheckSettings
        retry_timeout_sec,  # type: int
        source,  # type: Optional[Text]
    ):
        # type: (...) -> EyesScreenshot

        start = datetime.now()  # Start the retry timer.
        retry = datetime_utils.to_ms((datetime.now() - start).seconds)

        # The match retry loop.
        screenshot = self._taking_screenshot_loop(
            user_inputs,
            region,
            check_settings,
            retry_timeout_sec,
            retry,
            start,
            source,
            None,
        )
        # If we're here because we haven't found a match yet, try once more
        if not self._match_result.as_expected:
            logger.info("Window mismatch. Retrying...")
            return self._try_take_screenshot(
                user_inputs, region, check_settings, source
            )
        return screenshot

    def _taking_screenshot_loop(
        self,
        user_inputs,  # type: UserInputs
        region,  # type: Region
        check_settings,  # type: CheckSettings
        retry_timeout_ms,  # type: int
        retry_ms,  # type: int
        start,  # type: datetime
        source,  # type: Optional[Text]
        screenshot,  # type: Optional[EyesScreenshot]
    ):
        # type: (...) -> Optional[EyesScreenshot]

        if retry_ms >= retry_timeout_ms:
            return screenshot

        datetime_utils.sleep(self._MATCH_INTERVAL_MS)

        new_screenshot = self._try_take_screenshot(
            user_inputs, region, check_settings, source
        )
        if self._match_result.as_expected:
            return new_screenshot

        retry_ms = (start - datetime.now()).seconds
        return self._taking_screenshot_loop(
            user_inputs,
            region,
            check_settings,
            retry_timeout_ms,
            retry_ms,
            start,
            source,
            new_screenshot,
        )
