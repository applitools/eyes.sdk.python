from __future__ import absolute_import

import time
import typing as tp
from struct import pack

# noinspection PyProtectedMember
from applitools.common import logger
from applitools.common.errors import OutOfBoundsError
from applitools.common.geometry import Region
from applitools.common.utils import general_utils

if tp.TYPE_CHECKING:
    from applitools.common.utils.custom_types import (
        Num,
        RunningSession,
        AppOutput,
        UserInputs,
        MatchResult,
    )
    from applitools.core.server_connector import ServerConnector
    from .eyes_base import EyesBase
    from .match import ImageMatchSettings
    from .capture import EyesScreenshot

__all__ = ("MatchWindowTask",)


# TODO: remove Eyes and Target dependencies from here


class MatchWindowTask(object):
    """
    Handles matching of output with the expected output
    (including retry and 'ignore mismatch' when needed).
    """

    MATCH_INTERVAL = 0.5

    MINIMUM_MATCH_TIMEOUT = 60  # Milliseconds

    def __init__(self, eyes, server_connector, running_session, default_retry_timeout):
        # type: (EyesBase, ServerConnector, RunningSession, Num) -> None
        """
        Ctor.

        :param eyes: The Eyes instance which created this task.
        :param server_connector: The agent connector to use for communication.
        :param running_session:  The current eyes session.
        :param default_retry_timeout: The default match timeout. (milliseconds)
        """
        self._eyes = eyes
        self._server_connector = server_connector
        self._running_session = running_session
        self._default_retry_timeout = (
            default_retry_timeout / 1000.0
        )  # type: Num # since we want the time in seconds.
        self._last_screenshot = None  # type: tp.Optional[EyesScreenshot]

    @staticmethod
    def _create_match_data_bytes(
        app_output,  # type: AppOutput
        user_inputs,  # type: UserInputs
        tag,  # type: tp.Text
        ignore_mismatch,  # type: bool
        screenshot,  # type: EyesScreenshot
        default_match_settings,  # type: ImageMatchSettings
        target,
        ignore=None,  # type: tp.Optional[tp.List]
        floating=None,  # type: tp.Optional[tp.List]
    ):
        # type: (...) -> bytes
        if ignore is None:
            ignore = []
        if floating is None:
            floating = []

        match_data = {
            "IgnoreMismatch": ignore_mismatch,
            "Options": {
                "Name": tag,
                "UserInputs": user_inputs,
                "ImageMatchSettings": {
                    "MatchLevel": default_match_settings.match_level,
                    "IgnoreCaret": target.values.ignore_caret,
                    "Exact": default_match_settings.exact_settings,
                    "Ignore": ignore,
                    "Floating": floating,
                },
                "IgnoreMismatch": ignore_mismatch,
                "Trim": {"Enabled": False},
            },
            "UserInputs": user_inputs,
            "AppOutput": app_output,
            "tag": tag,
        }
        match_data_json_bytes = general_utils.to_json(match_data).encode(
            "utf-8"
        )  # type: bytes
        match_data_size_bytes = pack(">L", len(match_data_json_bytes))  # type: bytes
        screenshot_bytes = screenshot.bytes  # type: bytes
        body = match_data_size_bytes + match_data_json_bytes + screenshot_bytes
        return body

    @staticmethod
    def _get_dynamic_regions(target, eyes_screenshot):
        ignore = []  # type: tp.List[Region]
        floating = []  # type: tp.List[Region]
        if target is not None:
            for region_wrapper in target.values.ignore_regions:
                try:
                    current_region = region_wrapper.get_region(eyes_screenshot)
                    ignore.append(current_region)
                except OutOfBoundsError as err:
                    logger.info(
                        "WARNING: Region specified by {} is out of bounds! {}".format(
                            region_wrapper, err
                        )
                    )
            for floating_wrapper in target.values.floating_regions:
                try:
                    current_floating = floating_wrapper.get_region(eyes_screenshot)
                    floating.append(current_floating)
                except OutOfBoundsError as err:
                    logger.info(
                        "WARNING: Floating region specified by {} is out of bounds! {}".format(
                            floating_wrapper, err
                        )
                    )
        return {"ignore": ignore, "floating": floating}

    def _prepare_match_data_for_window(
        self,
        tag,  # type: tp.Text
        user_inputs,  # type: UserInputs
        default_match_settings,  # type: ImageMatchSettings
        target,
        ignore_mismatch=False,
    ):
        # type: (...) -> bytes
        title = self._eyes._title
        # TODO: Refactor this
        if hasattr(self._eyes, "_hide_scrollbars_if_needed"):
            with self._eyes._hide_scrollbars_if_needed():  # type: ignore
                self._last_screenshot = self._eyes.get_screenshot(
                    hide_scrollbars_called=True
                )
        else:
            self._last_screenshot = self._eyes.get_screenshot()

        dynamic_regions = MatchWindowTask._get_dynamic_regions(
            target, self._last_screenshot
        )
        app_output = {"title": title, "screenshot64": None}  # type: AppOutput

        if self._eyes.send_dom:
            dom_json = self._eyes._try_capture_dom()
            if dom_json:
                dom_url = self._eyes._try_post_dom_snapshot(dom_json)
                if dom_url is None:
                    logger.warning("Failed to upload DOM. Skipping...")
                else:
                    app_output["DomUrl"] = dom_url

        logger.debug("AppOutput: {}".format(app_output))
        return self._create_match_data_bytes(
            app_output,
            user_inputs,
            tag,
            ignore_mismatch,
            self._last_screenshot,
            default_match_settings,
            target,
            dynamic_regions["ignore"],
            dynamic_regions["floating"],
        )

    def _run_with_intervals(self, prepare_match_data_options, retry_timeout):
        # type: (tp.Dict, Num) -> MatchResult
        """
        Includes retries in case the screenshot does not match.
        """
        logger.debug("Matching with intervals...")
        # We intentionally take the first screenshot before starting the timer,
        # to allow the page just a tad more time to stabilize.
        prepare_match_data_options = prepare_match_data_options.copy()
        prepare_match_data_options["ignore_mismatch"] = True
        data = self._prepare_match_data_for_window(**prepare_match_data_options)

        # Start the timer.
        start = time.time()
        logger.debug("First match attempt...")
        as_expected = self._server_connector.match_window(self._running_session, data)
        if as_expected:
            return {"as_expected": True, "screenshot": self._last_screenshot}
        retry = time.time() - start
        logger.debug("Failed. Elapsed time: {0:.1f} seconds".format(retry))

        while retry < retry_timeout:
            logger.debug("Matching...")
            time.sleep(self.MATCH_INTERVAL)

            data = self._prepare_match_data_for_window(**prepare_match_data_options)
            as_expected = self._server_connector.match_window(
                self._running_session, data
            )
            if as_expected:
                return {"as_expected": True, "screenshot": self._last_screenshot}
            retry = time.time() - start
            logger.debug("Elapsed time: {0:.1f} seconds".format(retry))

        # One last try
        logger.debug("One last matching attempt...")
        prepare_match_data_options["ignore_mismatch"] = False
        data = self._prepare_match_data_for_window(**prepare_match_data_options)
        as_expected = self._server_connector.match_window(self._running_session, data)
        return {"as_expected": as_expected, "screenshot": self._last_screenshot}

    def match_window(
        self,
        retry_timeout,  # type: Num
        tag,  # type: str
        user_inputs,  # UserInputs
        default_match_settings,  # type: ImageMatchSettings
        target,
        ignore_mismatch,
        run_once_after_wait=False,
    ):
        # type: (...) -> MatchResult
        """
        Performs a match for the window.

        :param retry_timeout: Amount of time until it retries.
        :param tag: The name of the tag (optional).
        :param user_inputs: The user input.
        :param default_match_settings: The default match settings for the session.
        :param target: The target of the check_window call.
        :param ignore_mismatch: True if the server should ignore a negative result
                                for the visual validation.
        :param run_once_after_wait: Whether or not to run again after waiting.
        :return: The result of the run.
        """
        prepare_match_data_options = dict(
            tag=tag,
            user_inputs=user_inputs,
            default_match_settings=default_match_settings,
            target=target,
            ignore_mismatch=ignore_mismatch,
        )

        if 0 < retry_timeout < MatchWindowTask.MINIMUM_MATCH_TIMEOUT:
            raise ValueError(
                "Match timeout must be at least 60ms, got {} instead.".format(
                    retry_timeout
                )
            )
        if retry_timeout < 0:
            retry_timeout = self._default_retry_timeout
        else:
            retry_timeout /= 1000.0

        logger.debug("Match timeout set to: {0} seconds".format(retry_timeout))
        start = time.time()
        if run_once_after_wait or retry_timeout == 0:
            logger.debug("Matching once...")
            # If the load time is 0, the sleep would immediately return anyway.
            time.sleep(retry_timeout)
            data = self._prepare_match_data_for_window(**prepare_match_data_options)
            as_expected = self._server_connector.match_window(
                self._running_session, data
            )
            result = {
                "as_expected": as_expected,
                "screenshot": self._last_screenshot,
            }  # type: MatchResult
        else:
            result = self._run_with_intervals(prepare_match_data_options, retry_timeout)

        logger.debug("Match result: {0}".format(result["as_expected"]))
        elapsed_time = time.time() - start
        logger.debug("_run(): Completed in {0:.1f} seconds".format(elapsed_time))
        return result
