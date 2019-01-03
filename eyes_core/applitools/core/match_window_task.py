from __future__ import absolute_import

import functools
import time
import typing as tp
from struct import pack

# noinspection PyProtectedMember
from . import logger
from .utils import general_utils
from .errors import OutOfBoundsError
from .geometry import Region

if tp.TYPE_CHECKING:
    from .eyes_base import EyesBase
    from .utils.custom_types import (Num, RunningSession, AppOutput,
                                     UserInputs, MatchResult)
    from .agent_connector import AgentConnector
    from .match import ImageMatchSettings
    from .capture import EyesScreenshot

__all__ = ('MatchWindowTask',)


# TODO: remove Eyes and Target dependencies from here

class MatchWindowTask(object):
    """
    Handles matching of output with the expected output (including retry and 'ignore mismatch' when needed).
    """
    _MATCH_INTERVAL = 0.5

    MINIMUM_MATCH_TIMEOUT = 60  # Milliseconds

    def __init__(self, eyes, agent_connector, running_session, default_retry_timeout):
        # type: (EyesBase, AgentConnector, RunningSession, Num) -> None
        """
        Ctor.

        :param eyes: The Eyes instance which created this task.
        :param agent_connector: The agent connector to use for communication.
        :param running_session:  The current eyes session.
        :param default_retry_timeout: The default match timeout. (milliseconds)
        """
        self._eyes = eyes
        self._agent_connector = agent_connector
        self._running_session = running_session
        self._default_retry_timeout = default_retry_timeout / 1000.0  # type: Num # since we want the time in seconds.
        self._screenshot = None  # type: tp.Optional[EyesScreenshot]

    @staticmethod
    def _create_match_data_bytes(app_output,  # type: AppOutput
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
            "Options":        {
                "Name":               tag,
                "UserInputs":         user_inputs,
                "ImageMatchSettings": {
                    "MatchLevel":  default_match_settings.match_level,
                    "IgnoreCaret": target.ignore_caret,
                    "Exact":       default_match_settings.exact_settings,
                    "Ignore":      ignore,
                    "Floating":    floating
                },
                "IgnoreMismatch":     ignore_mismatch,
                "Trim":               {
                    "Enabled": False
                }
            },
            "UserInputs":     user_inputs,
            "AppOutput":      app_output,
            "tag":            tag
        }
        match_data_json_bytes = general_utils.to_json(match_data).encode('utf-8')  # type: bytes
        match_data_size_bytes = pack(">L", len(match_data_json_bytes))  # type: bytes
        screenshot_bytes = screenshot.get_bytes()
        body = match_data_size_bytes + match_data_json_bytes + screenshot_bytes
        return body

    @staticmethod
    def _get_dynamic_regions(target, eyes_screenshot):
        ignore = []  # type: tp.List[Region]
        floating = []  # type: tp.List[Region]
        if target is not None:
            for region_wrapper in target._ignore_regions:
                try:
                    current_region = region_wrapper.get_region(eyes_screenshot)
                    ignore.append(current_region)
                except OutOfBoundsError as err:
                    logger.info("WARNING: Region specified by {} is out of bounds! {}".format(region_wrapper, err))
            for floating_wrapper in target._floating_regions:
                try:
                    current_floating = floating_wrapper.get_region(eyes_screenshot)
                    floating.append(current_floating)
                except OutOfBoundsError as err:
                    logger.info("WARNING: Floating region specified by {} is out of bounds! {}".format(floating_wrapper,
                                                                                                       err))
        return {"ignore": ignore, "floating": floating}

    def _prepare_match_data_for_window(self, tag,  # type: tp.Text
                                       user_inputs,  # type: UserInputs
                                       default_match_settings,  # type: ImageMatchSettings
                                       target,
                                       ignore_mismatch=False):
        # type: (...) -> bytes
        title = self._eyes._title
        # TODO: Refactor this
        if hasattr(self._eyes, '_hide_scrollbars_if_needed'):
            with self._eyes._hide_scrollbars_if_needed():  # type: ignore
                self._screenshot = self._eyes.get_screenshot(hide_scrollbars_called=True)
        else:
            self._screenshot = self._eyes.get_screenshot()

        dynamic_regions = MatchWindowTask._get_dynamic_regions(target, self._screenshot)
        app_output = {'_title': title, 'screenshot64': None}  # type: AppOutput

        if self._eyes.send_dom:
            dom_json = self._eyes._try_capture_dom()
            if dom_json:
                dom_url = self._eyes._try_post_dom_snapshot(dom_json)
                if dom_url is None:
                    logger.warning('Failed to upload DOM. Skipping...')
                else:
                    app_output['DomUrl'] = dom_url

        logger.debug('AppOutput: {}'.format(app_output))
        return self._create_match_data_bytes(app_output, user_inputs, tag, ignore_mismatch,
                                             self._screenshot, default_match_settings, target,
                                             dynamic_regions['ignore'], dynamic_regions['floating'])

    def _run_with_intervals(self, prepare_action, retry_timeout):
        # type: (tp.Callable, Num) -> MatchResult
        """
        Includes retries in case the screenshot does not match.
        """
        logger.debug('Matching with intervals...')
        # We intentionally take the first screenshot before starting the timer, to allow the page
        # just a tad more time to stabilize.
        data = prepare_action()
        # Start the timer.
        start = time.time()
        logger.debug('First match attempt...')
        as_expected = self._agent_connector.match_window(self._running_session, data)
        if as_expected:
            return {"as_expected": True, "screenshot": self._screenshot}
        retry = time.time() - start
        logger.debug("Failed. Elapsed time: {0:.1f} seconds".format(retry))

        while retry < retry_timeout:
            logger.debug('Matching...')
            time.sleep(self._MATCH_INTERVAL)
            data = prepare_action()
            as_expected = self._agent_connector.match_window(self._running_session, data)
            if as_expected:
                return {"as_expected": True, "screenshot": self._screenshot}
            retry = time.time() - start
            logger.debug("Elapsed time: {0:.1f} seconds".format(retry))
        # One last try
        logger.debug('One last matching attempt...')
        data = prepare_action()
        as_expected = self._agent_connector.match_window(self._running_session, data)
        return {"as_expected": as_expected, "screenshot": self._screenshot}

    def _run(self, prepare_action, run_once_after_wait=False, retry_timeout=-1):
        # type: (tp.Callable, bool, Num) -> MatchResult
        if 0 < retry_timeout < MatchWindowTask.MINIMUM_MATCH_TIMEOUT:
            raise ValueError("Match timeout must be at least 60ms, got {} instead.".format(retry_timeout))
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
            data = prepare_action()
            as_expected = self._agent_connector.match_window(self._running_session, data)
            result = {"as_expected": as_expected, "screenshot": self._screenshot}  # type: MatchResult
        else:
            result = self._run_with_intervals(prepare_action, retry_timeout)
        logger.debug("Match result: {0}".format(result["as_expected"]))
        elapsed_time = time.time() - start
        logger.debug("_run(): Completed in {0:.1f} seconds".format(elapsed_time))
        return result

    def match_window(self, retry_timeout,  # type: Num
                     tag,  # type: str
                     user_inputs,  # UserInputs
                     default_match_settings,  # type: ImageMatchSettings
                     target,
                     ignore_mismatch,
                     run_once_after_wait=False):
        # type: (...) -> MatchResult
        """
        Performs a match for the window.

        :param retry_timeout: Amount of time until it retries.
        :param tag: The name of the tag (optional).
        :param user_inputs: The user input.
        :param default_match_settings: The default match settings for the session.
        :param target: The target of the check_window call.
        :param ignore_mismatch: True if the server should ignore a negative result for the visual validation.
        :param run_once_after_wait: Whether or not to run again after waiting.
        :return: The result of the run.
        """
        prepare_action = functools.partial(self._prepare_match_data_for_window, tag,
                                           user_inputs, default_match_settings, target, ignore_mismatch)
        return self._run(prepare_action, run_once_after_wait, retry_timeout)
